# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-09 16:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_spirit', '0027_auto_20191007_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitytimespend',
            name='difference',
        ),
        migrations.RemoveField(
            model_name='activitytimespend',
            name='pausetime',
        ),
        migrations.RemoveField(
            model_name='activitytimespend',
            name='starttime',
        ),
        migrations.AddField(
            model_name='activitytimespend',
            name='time_spent',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='time_spent(ms)'),
        ),
    ]
