# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-15 21:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0054_auto_20190819_1809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='is_monetized',
            field=models.BooleanField(default=False, verbose_name='Is Monetized?'),
        ),
    ]
