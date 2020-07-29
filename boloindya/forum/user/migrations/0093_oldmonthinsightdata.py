# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-07-18 00:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import forum.user.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_user', '0092_insightdatadump'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldMonthInsightData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('for_year', models.PositiveIntegerField(choices=[(2019, 2019), (2020, 2020)], default=forum.user.models.current_year, verbose_name='year')),
                ('for_month', models.PositiveIntegerField(choices=[(1, b'January'), (2, b'Feburary'), (3, b'Macrh'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')], default=forum.user.models.previous_month, verbose_name='month')),
                ('insight_data', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_insight_data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
