# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-11 17:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_userkyc', '0005_auto_20190910_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalinfo',
            name='reject_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Reject Text'),
        ),
        migrations.AlterField(
            model_name='bankdetail',
            name='reject_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Reject Text'),
        ),
        migrations.AlterField(
            model_name='kycbasicinfo',
            name='reject_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Reject Text'),
        ),
        migrations.AlterField(
            model_name='kycdocument',
            name='reject_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Reject Text'),
        ),
    ]
