# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-11-10 23:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drf_spirit', '0049_databasecounter'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DatabaseCounter',
            new_name='DatabaseRecordCount',
        ),
    ]
