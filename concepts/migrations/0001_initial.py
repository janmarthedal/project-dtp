# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-24 11:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mathitems', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'db_table': 'concepts',
            },
        ),
        migrations.CreateModel(
            name='ConceptDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concepts.Concept')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mathitems.MathItem')),
            ],
            options={
                'db_table': 'concept_defs',
            },
        ),
        migrations.CreateModel(
            name='ConceptMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_count', models.IntegerField()),
                ('def_count', models.IntegerField()),
                ('concept', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='concepts.Concept')),
            ],
            options={
                'db_table': 'concept_meta',
            },
        ),
        migrations.CreateModel(
            name='ConceptReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concepts.Concept')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mathitems.MathItem')),
            ],
            options={
                'db_table': 'concept_refs',
            },
        ),
        migrations.CreateModel(
            name='ItemDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concepts', models.ManyToManyField(to='concepts.Concept')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='mathitems.MathItem')),
                ('uses', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='mathitems.MathItem')),
            ],
            options={
                'db_table': 'item_deps',
            },
        ),
        migrations.AlterUniqueTogether(
            name='itemdependency',
            unique_together=set([('item', 'uses')]),
        ),
        migrations.AlterUniqueTogether(
            name='conceptreference',
            unique_together=set([('item', 'concept')]),
        ),
        migrations.AlterUniqueTogether(
            name='conceptdefinition',
            unique_together=set([('item', 'concept')]),
        ),
    ]
