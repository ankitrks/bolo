# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-14 18:50
from __future__ import unicode_literals

from django.db import migrations


def user_model_content_type(apps, schema_editor):
    from ...core.conf import settings

    if not hasattr(settings, 'AUTH_USER_MODEL'):
        return

    user = apps.get_model(settings.AUTH_USER_MODEL)

    if user._meta.db_table == 'forum_user_user':
        app_label, model = settings.AUTH_USER_MODEL.split('.')
        content_types = apps.get_model('contenttypes.ContentType')
        (content_types.objects
         .filter(
            app_label='forum_user',
            model='User'.lower())
         .update(
            app_label=app_label,
            model=model.lower()))


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0008_auto_20161114_1707'),
    ]

    operations = [
        migrations.RunPython(user_model_content_type),
    ]
