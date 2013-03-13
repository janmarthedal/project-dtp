python manage.py dumpdata items | python -mjson.tool > items/fixtures/initial_data.json
python manage.py dumpdata refs | python -mjson.tool > refs/fixtures/initial_data.json
python manage.py dumpdata tags | python -mjson.tool > tags/fixtures/initial_data.json
python manage.py dumpdata users | python -mjson.tool > users/fixtures/initial_data.json
