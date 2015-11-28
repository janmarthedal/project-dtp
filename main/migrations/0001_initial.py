# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MathItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('item_type', models.CharField(max_length=1, choices=[('D', 'Definition'), ('T', 'Theorem'), ('P', 'Proof')])),
                ('body', models.TextField(blank=True)),
            ],
        ),
    ]
