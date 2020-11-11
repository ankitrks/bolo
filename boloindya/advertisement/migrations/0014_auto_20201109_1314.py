# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-11-09 13:14
from __future__ import unicode_literals

from django.db import migrations

from connection import dynamo_client

from advertisement.models import AdEvent, Counter

client = dynamo_client()

def create_dynamo_table(apps, schema_editor):
    response = client.create_table(
        TableName=AdEvent,
        AttributeDefinitions=[
            {
                'AttributeName': 'event',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'event',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'id',
                'KeyType': 'RANGE'
            }
        ],
        BillingMode='PAY_PER_REQUEST',
    )
    print "response", response

    response = client.create_table(
        TableName=Counter,
        AttributeDefinitions=[
            {
                'AttributeName': 'seq_name',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'seq_name',
                'KeyType': 'HASH'
            }
        ],
        BillingMode='PAY_PER_REQUEST',
    )
    print "response", response




class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0013_order_order_number'),
    ]

    operations = [
        migrations.RunPython(create_dynamo_table),
    ]
