# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-11-19 15:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drf_spirit', '0034_userfeedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfeedback',
            name='by_user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
