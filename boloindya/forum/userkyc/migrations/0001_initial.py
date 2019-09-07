# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-22 16:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('father_firstname', models.CharField(blank=True, max_length=255, verbose_name='Father First Name')),
                ('father_lastname', models.CharField(blank=True, max_length=255, verbose_name='Father Last Name')),
                ('mother_firstname', models.CharField(blank=True, max_length=255, verbose_name='Mother First Name')),
                ('mother_lastname', models.CharField(blank=True, max_length=255, verbose_name='Mother Last Name')),
                ('profession', models.CharField(blank=True, choices=[('1', 'Govermnet Employee'), ('2', 'Private Sector'), ('3', 'Business'), ('99', 'Others')], default='99', max_length=10, null=True)),
                ('status', models.CharField(blank=True, choices=[('1', 'Single'), ('2', 'Married'), ('3', 'Divorced')], default='1', max_length=10, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_userkyc_additionalinfo_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AdditionalInfo',
                'verbose_name_plural': "AdditionalInfo's",
            },
        ),
        migrations.CreateModel(
            name='BankDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('bank_name', models.CharField(blank=True, max_length=255, verbose_name='Bank Name')),
                ('account_number', models.CharField(blank=True, max_length=255, verbose_name='Account Number')),
                ('IFSC_code', models.CharField(blank=True, max_length=255, verbose_name='IFSC Code')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_userkyc_bankdetail_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'BankDetail',
                'verbose_name_plural': "BankDetail's",
            },
        ),
        migrations.CreateModel(
            name='KYCBasicInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('first_name', models.CharField(blank=True, max_length=255, verbose_name='First Name')),
                ('middle_name', models.CharField(blank=True, max_length=255, verbose_name='Middle Name')),
                ('lastname_name', models.CharField(blank=True, max_length=255, verbose_name='Last Name')),
                ('d_o_b', models.DateField(blank=True, null=True)),
                ('mobile_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='Mobile No')),
                ('is_mobile_verified', models.BooleanField(default=False)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('pic_selfie_url', models.CharField(blank=True, max_length=1000, verbose_name='Pic Selfie')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_userkyc_kycbasicinfo_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'KYCbasicInfo',
                'verbose_name_plural': "KYCbasicInfo's",
            },
        ),
        migrations.CreateModel(
            name='KYCDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('frontside_url', models.CharField(blank=True, max_length=1000, verbose_name='Document Front Url')),
                ('backside_url', models.CharField(blank=True, max_length=1000, verbose_name='Document Back Url')),
            ],
            options={
                'verbose_name': 'KYCDocument',
                'verbose_name_plural': "KYCDocument's",
            },
        ),
        migrations.CreateModel(
            name='KYCDocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('document_name', models.CharField(blank=True, max_length=255, verbose_name='Document Name')),
                ('no_image_required', models.PositiveIntegerField(blank=True, default=1, null=True)),
            ],
            options={
                'verbose_name': 'KYCDocumentType',
                'verbose_name_plural': "KYCDocumentType's",
            },
        ),
        migrations.CreateModel(
            name='UserKYC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('kyc_basic_info_submitted', models.BooleanField(default=False)),
                ('is_kyc_basic_info_accepted', models.BooleanField(default=False)),
                ('kyc_document_info_submitted', models.BooleanField(default=False)),
                ('is_kyc_document_info_accepted', models.BooleanField(default=False)),
                ('kyc_pan_info_submitted', models.BooleanField(default=False)),
                ('is_kyc_pan_info_accepted', models.BooleanField(default=False)),
                ('kyc_selfie_info_submitted', models.BooleanField(default=False)),
                ('is_kyc_selfie_info_accepted', models.BooleanField(default=False)),
                ('kyc_additional_info_submitted', models.BooleanField(default=False)),
                ('is_kyc_additional_info_accepted', models.BooleanField(default=False)),
                ('is_kyc_completed', models.BooleanField(default=False)),
                ('is_kyc_accepted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_userkyc_userkyc_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-is_kyc_accepted'],
                'verbose_name': 'UserKyc',
                'verbose_name_plural': "UserKYC's",
            },
        ),
        migrations.AddField(
            model_name='kycdocument',
            name='kyc_document_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='forum_userkyc.KYCDocumentType'),
        ),
        migrations.AddField(
            model_name='kycdocument',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_userkyc_kycdocument_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
