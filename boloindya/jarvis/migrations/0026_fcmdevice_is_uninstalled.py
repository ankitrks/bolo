# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-12-09 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0025_auto_20191204_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='fcmdevice',
            name='is_uninstalled',
            field=models.BooleanField(default=False),
        ),
    ]
