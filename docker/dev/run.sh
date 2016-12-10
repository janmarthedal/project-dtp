docker run -t -v $PWD/../..:/code -w /code -p 8000:8000 --rm --name mathitem-dev janmarthedal/py3node sh -c ". env/bin/activate && python manage.py runserver 0.0.0.0:8000"
