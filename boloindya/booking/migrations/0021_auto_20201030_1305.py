# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-10-30 13:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '0020_booking_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventBookingInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('igst_percentage', models.DecimalField(decimal_places=2, default=18.0, max_digits=10)),
                ('net_amount_payble', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_mode', models.TextField(blank=True, null=True)),
                ('discount', models.PositiveIntegerField(default=0)),
                ('invoice_pdf_url', models.TextField(blank=True, null=True)),
                ('consumer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_event_booking_invoice', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='eventbooking',
            name='invoice_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='eventbookinginvoice',
            name='event_booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_booking_invoice', to='booking.EventBooking'),
        ),
        migrations.AddField(
            model_name='eventbookinginvoice',
            name='event_creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator_event_booking_invoice', to=settings.AUTH_USER_MODEL),
        ),
    ]
