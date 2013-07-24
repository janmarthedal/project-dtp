python ../manage.py dumpdata --indent 2 users tags items sources > ../backups/dump-`date -u +%FT%R`.json
