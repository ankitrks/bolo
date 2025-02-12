# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import forum.core.utils.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum_category', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('slug', forum.core.utils.models.AutoSlugField(blank=True, db_index=False, populate_from='title')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date')),
                ('last_active', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last active')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='pinned')),
                ('is_globally_pinned', models.BooleanField(default=False, verbose_name='globally pinned')),
                ('is_closed', models.BooleanField(default=False, verbose_name='closed')),
                ('is_removed', models.BooleanField(default=False)),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='views count')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='comment count')),
                ('category', models.ForeignKey(to='forum_category.Category', verbose_name='category')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'topics',
                'ordering': ['-last_active', '-pk'],
                'verbose_name': 'topic',
            },
        ),
    ]
