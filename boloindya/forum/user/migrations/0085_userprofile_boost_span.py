# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-06-29 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0084_duser'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='boost_span',
            field=models.PositiveIntegerField(default=0, verbose_name='Boost Span(Days)'),
        ),
    ]
