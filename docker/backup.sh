docker exec docker_app_1 python3 manage.py dumpdata -e sessions -e auth.permission -e contenttypes > data.json
