# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ItemReference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('concept', models.ForeignKey(to='main.Concept', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MathItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('item_type', models.CharField(max_length=1, choices=[('D', 'Definition'), ('T', 'Theorem'), ('P', 'Proof')])),
                ('body', models.TextField(blank=True)),
                ('concepts_defined', models.ManyToManyField(related_name='_mathitem_concepts_defined_+', to='main.Concept')),
                ('concepts_referenced', models.ManyToManyField(related_name='_mathitem_concepts_referenced_+', to='main.Concept')),
                ('items_referenced', models.ManyToManyField(to='main.MathItem', through='main.ItemReference')),
            ],
        ),
        migrations.AddField(
            model_name='itemreference',
            name='from_mathitem',
            field=models.ForeignKey(related_name='+', to='main.MathItem'),
        ),
        migrations.AddField(
            model_name='itemreference',
            name='to_mathitem',
            field=models.ForeignKey(related_name='+', to='main.MathItem'),
        ),
    ]
