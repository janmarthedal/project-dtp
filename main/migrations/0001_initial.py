# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DraftItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('item_type', models.CharField(choices=[('D', 'Definition'), ('T', 'Theorem'), ('P', 'Proof')], max_length=1)),
                ('body', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Equation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MathItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item_type', models.CharField(choices=[('D', 'Definition'), ('T', 'Theorem'), ('P', 'Proof')], max_length=1)),
                ('body', models.TextField(blank=True)),
            ],
        ),
    ]
