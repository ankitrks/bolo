# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-06-21 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0083_userprofile_country_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='salary_range',
            field=models.CharField(blank=True, choices=[(b'1', b'Less than 20000'), (b'2', b'20000 - 40000'), (b'3', b'40000 - 60000'), (b'4', b'Greater than 60000')], db_index=True, max_length=10, null=True),
        ),
    ]
