# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-04-13 20:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0077_userprofile_paytm_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'user profile', 'verbose_name_plural': 'user profiles'},
        ),
        migrations.AddField(
            model_name='referralcode',
            name='download_count',
            field=models.PositiveIntegerField(default=0, verbose_name='ownload count'),
        ),
        migrations.AddField(
            model_name='referralcode',
            name='signup_count',
            field=models.PositiveIntegerField(default=0, verbose_name='signup count'),
        ),
    ]
