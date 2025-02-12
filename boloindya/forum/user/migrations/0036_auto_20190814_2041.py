# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-14 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0035_auto_20190814_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referralcode',
            name='campaign_url',
            field=models.CharField(blank=True, editable=False, max_length=350, null=True, verbose_name='Playstore URL'),
        ),
        migrations.AlterField(
            model_name='referralcode',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='live'),
        ),
    ]
