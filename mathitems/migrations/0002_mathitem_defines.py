# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-04 18:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mathitems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mathitem',
            name='defines',
            field=models.ManyToManyField(to='mathitems.Concept'),
        ),
    ]
