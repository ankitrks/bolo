# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-19 16:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0041_auto_20190917_1634'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DeltaAndroidLogs',
        ),
    ]
