# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-10-09 19:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_booking_thumbnail_img_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='available_slots',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
