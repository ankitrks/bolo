# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-14 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0034_auto_20190814_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='referralcode',
            name='campaign_url',
            field=models.CharField(blank=True, max_length=350, null=True, verbose_name='Campaign URL'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='d_o_b',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Date of Birth'),
        ),
    ]
