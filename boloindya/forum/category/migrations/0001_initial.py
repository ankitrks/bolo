# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import forum.core.utils.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='title', max_length=75)),
                ('slug', forum.core.utils.models.AutoSlugField(db_index=False, populate_from='title', blank=True)),
                ('description', models.CharField(verbose_name='description', max_length=255, blank=True)),
                ('is_closed', models.BooleanField(verbose_name='closed', default=False)),
                ('is_removed', models.BooleanField(verbose_name='removed', default=False)),
                ('is_private', models.BooleanField(verbose_name='private', default=False)),
                ('parent', models.ForeignKey(null=True, verbose_name='category parent', to='forum_category.Category', blank=True)),
            ],
            options={
                'ordering': ['title', 'pk'],
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
    ]
