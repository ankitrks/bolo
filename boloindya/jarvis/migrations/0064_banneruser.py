# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-04-14 14:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jarvis', '0063_auto_20200413_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('hash_tag', models.CharField(blank=True, max_length=1000, null=True, verbose_name='hash_tag')),
                ('response_type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Response Type')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='banner_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
