# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-03 18:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drf_spirit', '0003_singupotp_is_for_change_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserJarvisDump',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dump', models.TextField(blank=True, null=True, verbose_name='User Dump')),
                ('dump_type', models.CharField(choices=[(b'1', b'user_activities_data'), (b'2', b'error_logs')], max_length=50, verbose_name='Dump Type')),
                ('sync_time', models.DateTimeField(auto_now_add=True, verbose_name='Sync Time')),
                ('user', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
