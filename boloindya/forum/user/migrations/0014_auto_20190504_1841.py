# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-04 18:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0013_userprofile_mobile_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='st', to=settings.AUTH_USER_MODEL, verbose_name='profile'),
        ),
    ]
