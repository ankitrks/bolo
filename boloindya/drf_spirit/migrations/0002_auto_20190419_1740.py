# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-19 17:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drf_spirit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='singupotp',
            name='api_response_dump',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='singupotp',
            name='for_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='singupotp',
            name='is_reset_password',
            field=models.BooleanField(default=False, verbose_name='is reset password?'),
        ),
    ]
