# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-09 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_category', '0007_auto_20190407_1600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order_no'], 'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.AddField(
            model_name='category',
            name='order_no',
            field=models.IntegerField(default=0),
        ),
    ]
