# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-01-28 23:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum_category', '0017_categoryviewcounter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoryviewcounter',
            options={'ordering': ['language']},
        ),
    ]
