# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-06-20 13:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0102_topic_profnity_retry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='profnity_retry',
        ),
    ]
