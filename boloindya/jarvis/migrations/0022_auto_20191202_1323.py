# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-12-02 13:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0021_auto_20191130_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushnotification',
            name='language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada')], default='0', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='statedistrictlanguage',
            name='district_language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada')], default='1', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='statedistrictlanguage',
            name='state_language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada')], default='1', max_length=10, null=True),
        ),
    ]
