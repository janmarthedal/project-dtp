#!/bin/bash

PYTHON=/usr/local/bin/python3.3
export PYTHONPATH=/home/jmr/webapps/teoremer_django/teoremer:/home/jmr/lib/python3.3
LOG=/home/jmr/webapps/teoremer_django/logs/cron.log

cd /home/jmr/webapps/teoremer_django/teoremer
echo >> $LOG
echo "Maintenance `date`" >> $LOG
echo "* clearsessions" >> $LOG
$PYTHON manage.py clearsessions 2>&1 >> $LOG
echo "* deps" >> $LOG
$PYTHON manage.py deps 2>&1 >> $LOG
echo "* points" >> $LOG
$PYTHON manage.py points 2>&1 >> $LOG
echo "Maintenance done" >> $LOG
