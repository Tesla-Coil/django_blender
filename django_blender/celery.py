import importlib
import os

from celery import Celery
from celery.signals import worker_init
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blender.settings')


@worker_init.connect
def init_blender(worker, **kwargs):
    if not settings.BLENDER_USE_GPU:
        get_blender()


def get_blender(filepath=settings.BLENDER_FILE, new_instance=False):
    import sys
    if 'bpy' not in sys.modules or new_instance:
        bpy = importlib.import_module('bpy')
        bpy.ops.wm.open_mainfile(filepath=filepath)
        preferences = bpy.context.user_preferences.addons['cycles'].preferences
        preferences.compute_device_type = settings.BLENDER_GPU_DEVICE if settings.BLENDER_USE_GPU else 'NONE'
    return sys.modules['bpy']


app = Celery('django_blender')


app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
