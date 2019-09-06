# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-04 17:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_payment', '0003_auto_20190903_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encashabledetail',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_payment_encashabledetail_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='paymentinfo',
            name='enchashable_detail',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='forum_payment.EncashableDetail'),
        ),
        migrations.AlterField(
            model_name='paymentinfo',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_payment_paymentinfo_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
