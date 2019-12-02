# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-11-30 18:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0066_auto_20191129_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='language_id',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'4', b'Kannada')], default='1', max_length=10, null=True, verbose_name='language'),
        ),
    ]
