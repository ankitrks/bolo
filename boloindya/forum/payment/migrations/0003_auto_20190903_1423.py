# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-03 14:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum_payment', '0002_encashabledetail_bolo_score_details'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentinfo',
            old_name='encashble_detail',
            new_name='enchashable_detail',
        ),
    ]
