# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-04-17 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0092_tonguetwister_is_blocked'),
    ]

    operations = [
        migrations.CreateModel(
            name='RankingWeight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('features', models.CharField(max_length=20)),
                ('weight', models.FloatField(default=0, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='topic',
            name='vb_score',
            field=models.PositiveIntegerField(blank=True, db_index=True, default=0, null=True, verbose_name='VB Score'),
        ),
    ]
