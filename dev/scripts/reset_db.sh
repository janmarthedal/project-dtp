echo "drop database if exists thrms; create database thrms character set utf8;" | mysql -u root -p
python ../../manage.py syncdb --noinput
