# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-09-11 20:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0097_userprofile_is_bot_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='android_did',
            field=models.CharField(blank=True, db_index=True, max_length=200, null=True, verbose_name='android_did'),
        ),
    ]
