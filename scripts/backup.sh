python ../manage.py dumpdata --indent 2 users tags drafts items sources > ../backups/dump-`date -u +%FT%R`.json
