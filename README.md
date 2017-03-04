# Blender as module with Django Channels and Celery
This example shows how using Blender as Python module in Django project with Celery to task queuing.
Demo video: https://www.youtube.com/watch?v=42nvLjOv8Ng

# Building dependencies and setup environment
## Custom Python build with enable-shared
```
wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
tar -xvf Python-3.5.2.tgz
cd Python-3.5.2
./configure --prefix=/opt/py35 --enable-shared
sudo make install
```
## Create virtual environment for project
```
/opt/py35/bin/python3 -m venv ~/django-blender-env
```

## Build Blender as module
Get source
```
mkdir ~/blender-git
cd ~/blender-git
git clone https://git.blender.org/blender.git
cd blender
git submodule update --init --recursive
git submodule foreach git checkout master
git submodule foreach git pull --rebase origin master
```
Build Blender dependencies
```
cd ~/blender-git
./blender/build_files/build_environment/install_deps.sh
```
Compile Blender
```
mkdir ~/blender-git/build
cd ~/blender-git/build
cmake ../blender -DWITH_PYTHON_INSTALL=OFF -DWITH_PLAYER=OFF -DWITH_PYTHON_MODULE=ON -DCMAKE_INSTALL_PREFIX=$HOME/django-blender-env/lib/python3.5/site-packages
make
make install
```
## Setup Project
Make sure that you have installed Redis
```
sudo add-apt-repository ppa:chris-lea/redis-server
sudo apt-get update
sudo apt-get install redis-server
```
Clone and install dependencies in virtual environment 
```
cd ~/django-blender-env
source bin/activate
git clone https://github.com/hophead-ninja/django_blender.git
cd django_blender
pip install -r requirements.txt
```
Django migrations
```
python manage.py makemigrations
python manage.py migrate
```

# Run
Run server
```
python manage.py runserver
```
Run worker
```
celery worker -A django_blender -l info
```