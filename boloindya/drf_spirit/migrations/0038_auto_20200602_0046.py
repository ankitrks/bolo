# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-06-02 00:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0100_topic_safe_backup_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drf_spirit', '0037_auto_20200508_0105'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('banner_img_url', models.TextField(verbose_name='Banner Image URL')),
                ('is_active', models.BooleanField(default=True)),
                ('active_from', models.DateTimeField(verbose_name='Active From')),
                ('active_till', models.DateTimeField(verbose_name='Active Till')),
                ('is_winner_declared', models.BooleanField(default=False)),
                ('hashtag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_hashtag', to='forum_topic.TongueTwister', verbose_name='HashTag')),
                ('next_campaign_hashtag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campaign_next_hashtag', to='forum_topic.TongueTwister', verbose_name='NextCampaignHashTag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Winner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('rank', models.PositiveSmallIntegerField(verbose_name='Rank')),
                ('extra_text', models.TextField(blank=True, null=True, verbose_name='Extra Text')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='winner_user', to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='winner_video', to='forum_topic.Topic', verbose_name='Video')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='winners',
            field=models.ManyToManyField(blank=True, related_name='m2mwinner_campaign', to='drf_spirit.Winner', verbose_name='winner'),
        ),
    ]
