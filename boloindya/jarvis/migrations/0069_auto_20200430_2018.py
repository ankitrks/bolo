# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-04-30 20:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0068_merge_20200428_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercountnotification',
            options={'verbose_name': 'UserCountNotification', 'verbose_name_plural': 'UserCountNotifications'},
        ),
    ]
