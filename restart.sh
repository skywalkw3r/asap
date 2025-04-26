podman stop provisioning-portal # stop pod
podman rm provisioning-portal # remove pod
cd /Users/lucas/ownCloud/Documents/code/asap/ # cd to project
source venv/bin/activate # activate python virtual env
python manage.py migrate # ensure migrations are done for local DB
python manage.py runserver # run app