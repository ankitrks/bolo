# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-12-11 15:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0072_auto_20191205_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.TextField(blank=True, null=True, verbose_name='title')),
                ('hash_tags', models.ManyToManyField(blank=True, related_name='hash_tag_topics_history', to='forum_topic.TongueTwister', verbose_name='hash_tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.TextField(blank=True, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='topichistory',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_history', to='forum_topic.Topic'),
        ),
    ]
