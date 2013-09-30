mysql -u root -p < "drop database if exists thrms; create database thrms character set utf8;"
python ../../manage.py syncdb --noinput
