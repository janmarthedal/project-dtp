# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-29 13:32
from __future__ import unicode_literals

from django.db import migrations


def populate(apps, schema_editor):
    Concept = apps.get_model('concepts', 'Concept')
    Concept.objects.create(name='*')


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate),
    ]
