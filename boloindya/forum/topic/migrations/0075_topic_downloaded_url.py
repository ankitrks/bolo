# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-01-06 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0075_auto_20200107_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='downloaded_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='downloaded URL'),
        ),
    ]
