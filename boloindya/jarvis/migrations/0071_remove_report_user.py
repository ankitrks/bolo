# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-15 01:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0070_merge_20200515_0153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='user',
        ),
    ]
