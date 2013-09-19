mysql -u root -p < clear_db.sql
python ../../manage.py syncdb --noinput
