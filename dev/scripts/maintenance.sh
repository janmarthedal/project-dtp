#!/bin/bash

PYTHON=/usr/local/bin/python2.7
export PYTHONPATH=/home/jmr/webapps/thrms_django/teoremer:/home/jmr/lib/python2.7

cd /home/jmr/webapps/thrms_django/teoremer
echo >> log/cron.log
echo "Maintenance `date`" >> log/cron.log
echo "* clearsessions" >> log/cron.log
$PYTHON manage.py clearsessions 2>&1 >> log/cron.log
echo "* deps" >> log/cron.log
$PYTHON manage.py deps 2>&1 >> log/cron.log
echo "* points" >> log/cron.log
$PYTHON manage.py points 2>&1 >> log/cron.log
echo "Maintenance done" >> log/cron.log
