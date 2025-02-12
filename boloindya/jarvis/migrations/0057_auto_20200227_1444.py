# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-27 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0056_merge_20200227_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardmetricsjarvis',
            name='category_slab_options',
            field=models.CharField(blank=True, choices=[(b'71', b'Lifestyle and Travel'), (b'68', b'Fitness'), (b'70', b'Fashion and Beauty'), (b'73', b'Shopping / Reviews'), (b'63', b'General Knowledge'), (b'69', b'Food and Cooking'), (b'75', b'Finance Knowledge'), (b'77', b'Story Telling'), (b'67', b'Health'), (b'65', b'Motivation'), (b'72', b'Technology'), (b'74', b'Entertainment'), (b'60', b'Sports'), (b'66', b'Relationships'), (b'76', b'English Learning'), (b'64', b'Entrance Exams'), (b'62', b'Career and Jobs'), (b'61', b'Open Podcasts'), (b'78', b'Astrology'), (b'79', b'Religion'), (b'58', b'Parent')], default='0', max_length=10, null=True),
        ),
    ]
