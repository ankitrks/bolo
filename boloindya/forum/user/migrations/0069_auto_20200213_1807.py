# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-13 18:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0068_merge_20200205_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='slug',
            field=models.CharField(blank=True, max_length=100, verbose_name='slug'),
        ),
    ]
