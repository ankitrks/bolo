# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-28 16:46
from __future__ import unicode_literals

from django.db import migrations

def combine_category(apps, schema_editor):
	jarvis_models = apps.get_model('jarvis', 'DashboardMetricsJarvis')
	for each_row in jarvis_models.objects.all():
		if((each_row.category_slab_options!='None') and (each_row.category_slab_options!='0')):
			each_row.category_id = int(each_row.category_slab_options)
			each_row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0056_dashboardmetricsjarvis_category'),
    ]

    operations = [
    	migrations.RunPython(combine_category, reverse_code=migrations.RunPython.noop),
    ]
