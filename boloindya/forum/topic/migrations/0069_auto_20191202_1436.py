# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-12-02 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0068_auto_20191202_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='tonguetwister',
            name='gj_descpription',
            field=models.TextField(blank=True, null=True, verbose_name='Gujrati Hash Tag Description'),
        ),
        migrations.AddField(
            model_name='tonguetwister',
            name='ma_descpription',
            field=models.TextField(blank=True, null=True, verbose_name='Malyalam Hash Tag Description'),
        ),
        migrations.AddField(
            model_name='tonguetwister',
            name='mt_descpription',
            field=models.TextField(blank=True, null=True, verbose_name='Marathi Hash Tag Description'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='language_id',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi')], default='1', max_length=10, null=True, verbose_name='language'),
        ),
    ]
