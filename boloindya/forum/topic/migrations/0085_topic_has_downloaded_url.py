# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-11 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0084_auto_20200205_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='has_downloaded_url',
            field=models.BooleanField(default=False),
        ),
    ]
