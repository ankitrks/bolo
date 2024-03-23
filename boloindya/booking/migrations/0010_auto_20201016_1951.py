# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-10-16 19:51
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_category', '0022_auto_20200709_1303'),
        ('forum_topic', '0119_auto_20200916_0028'),
        ('booking', '0009_auto_20201016_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_booking', to='forum_category.Category'),
        ),
        migrations.AddField(
            model_name='booking',
            name='hash_tags',
            field=models.ManyToManyField(blank=True, related_name='hash_tag_bookings', to='forum_topic.TongueTwister'),
        ),
        migrations.AddField(
            model_name='booking',
            name='language_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None),
        ),
    ]
