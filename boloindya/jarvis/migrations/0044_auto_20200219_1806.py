# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-19 18:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0043_fcmdevice_current_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fcmdevice',
            name='current_version',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='fcmdevice',
            name='device_model',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='fcmdevice',
            name='manufacturer',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]
