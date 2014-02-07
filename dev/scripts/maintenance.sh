#!/bin/bash

PYTHON=/usr/local/bin/python2.7
export PYTHONPATH=/home/jmr/webapps/thrms_django/teoremer:/home/jmr/lib/python2.7
LOG=/home/jmr/webapps/thrms_django/log/cron.log

cd /home/jmr/webapps/thrms_django/teoremer
echo >> $LOG
echo "Maintenance `date`" >> $LOG
echo "* clearsessions" >> $LOG
$PYTHON manage.py clearsessions 2>&1 >> $LOG
echo "* deps" >> $LOG
$PYTHON manage.py deps 2>&1 >> $LOG
echo "* points" >> $LOG
$PYTHON manage.py points 2>&1 >> $LOG
echo "Maintenance done" >> $LOG
