# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-12 07:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_svgimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='CindyMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=128)),
                ('version', models.CharField(max_length=16)),
                ('aspect_ratio', models.FloatField()),
                ('data', models.TextField()),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='media.Media')),
            ],
            options={
                'db_table': 'cindymedia',
            },
        ),
    ]