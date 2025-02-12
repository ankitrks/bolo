# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-07 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0027_auto_20190805_1601'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppPageContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('page_name', models.CharField(blank=True, max_length=100, verbose_name='Page Name')),
                ('page_description', models.TextField(blank=True, null=True, verbose_name='Page Description')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
