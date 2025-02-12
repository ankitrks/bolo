# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-28 18:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_user', '0074_auto_20200318_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('contact_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Contact Name')),
                ('contact_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Contact Number')),
                ('contact_email', models.CharField(blank=True, max_length=200, null=True, verbose_name='Contact Email')),
                ('is_user_registered', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserPhoneBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('contact', models.ManyToManyField(related_name='forum_user_userphonebook_contact', to='forum_user.Contact', verbose_name='Contact')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='phonebook', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='referralcode',
            name='is_refer_earn_code',
            field=models.BooleanField(default=False, verbose_name='Is Refer Earn Code?'),
        ),
    ]
