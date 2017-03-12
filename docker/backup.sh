docker-compose run --rm app python manage.py dumpdata -e contenttypes -e auth -e sessions -e social_django \
  -e concepts.conceptdefinition -e concepts.conceptreference -e concepts.itemdependency -e equations.itemequation
