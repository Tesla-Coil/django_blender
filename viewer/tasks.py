import base64
import json
import os
import time
import threading

from django_blender.celery import app, get_blender
from channels import Channel
from django.conf import settings


@app.task(bind=True, track_started=True)
def render(task, data, reply_channel):
    bpy = get_blender()
    setup_scene(bpy, data)

    context = {'rendering': True, 'filepath': os.path.join(settings.BLENDER_RENDER_TMP_DIR, task.request.id)}
    sync_thread = threading.Thread(target=sync_render, args=(bpy, context, reply_channel))
    sync_thread.start()
    bpy.ops.render.render()
    context['rendering'] = False
    sync_thread.join()

    if os.path.exists(context['filepath']):
        os.remove(context['filepath'])

    if reply_channel is not None:
        Channel(reply_channel).send({
            'text': json.dumps({
                'action': 'render_finished'
            })
        })


def setup_scene(bpy, data):
    try:
        levels = int(data['subsurf'])
    except ValueError:
        levels = 0
    bpy.context.object.modifiers[0].render_levels = levels


def sync_render(bpy, context, reply_channel):
    while context['rendering']:
        time.sleep(settings.BLENDER_RENDER_SYNC_INTERVAL)

        image = bpy.data.images['Render Result']
        image.save_render(filepath=context['filepath'])

        with open(context['filepath'], "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        if reply_channel is not None:
            Channel(reply_channel).send({
                'text': json.dumps({
                    'action': 'sync_render',
                    'image': encoded_string.decode()
                })
            })
