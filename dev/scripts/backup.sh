python ../../manage.py dumpdata --indent 2 users tags drafts items sources default.UserSocialAuth document media > ../backup/dump-`date -u +%FT%R`.json
