# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-11-07 22:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0005_product_max_quantity_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='product_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='advertisement.Product'),
            preserve_default=False,
        ),
    ]
