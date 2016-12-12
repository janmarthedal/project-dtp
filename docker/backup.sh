docker-compose run --rm app python manage.py dumpdata -e sessions -e auth.permission -e contenttypes \
  -e concepts.conceptdefinition -e concepts.conceptreference -e concepts.itemdependency -e equations.itemequation
