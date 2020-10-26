# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-10-18 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0013_auto_20201017_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventbooking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='eventbooking',
            name='state',
            field=models.CharField(choices=[('draft', 'Draft'), ('booked', 'Booked'), ('cancelled', 'Cancelled')], default='draft', max_length=10),
        ),
    ]
