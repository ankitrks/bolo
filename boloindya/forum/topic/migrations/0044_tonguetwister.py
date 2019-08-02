# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-02 23:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0043_topic_m2mcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='TongueTwister',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_tag', models.CharField(blank=True, max_length=255, null=True, verbose_name='Hash Tag')),
                ('descpription', models.TextField(blank=True, null=True, verbose_name='Hash Tag Description')),
            ],
        ),
    ]
