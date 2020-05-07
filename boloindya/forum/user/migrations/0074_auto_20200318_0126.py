# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-18 01:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0073_auto_20200308_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='android_did',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='android_did'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_guest_user',
            field=models.BooleanField(default=False),
        ),
    ]
