# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-23 13:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drf_spirit', '0015_auto_20190923_1346'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='user_log_statistics',
            new_name='UserLogStatistics',
        ),
    ]
