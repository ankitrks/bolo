# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-06 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_comment', '0005_auto_20190406_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='thumbnail',
            field=models.CharField(default='', max_length=150, verbose_name='thumbnail'),
        ),
    ]
