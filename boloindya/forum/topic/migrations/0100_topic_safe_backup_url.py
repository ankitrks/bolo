# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-30 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0099_videodelete'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='safe_backup_url',
            field=models.TextField(blank=True, verbose_name='safe backup url'),
        ),
    ]
