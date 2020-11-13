# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-11-07 17:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_image', models.CharField(blank=True, max_length=200, null=True)),
                ('compressed_image', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='discounted_price',
        ),
        migrations.RemoveField(
            model_name='brand',
            name='product_category',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address_id',
        ),
        migrations.AddField(
            model_name='ad',
            name='ad_length',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ad',
            name='thumbnail',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='advertisement.Address'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending_for_approval', 'Pending for Approval'), ('accepted_by_vender', 'Accepted by vendor'), ('delivered', 'Delivered')], default='draft', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='currency',
            field=models.CharField(default='INR', max_length=10),
        ),
        migrations.AddField(
            model_name='product',
            name='is_discounted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='mrp',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=1, max_digits=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='rating_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ad',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='advertisement.Brand'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_ads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ad',
            name='frequency_type',
            field=models.CharField(choices=[('constant', 'Constant'), ('variable', 'Variable')], default='constant', max_length=25),
        ),
        migrations.AlterField(
            model_name='ad',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modify_ads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ad',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='advertisement.Product'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='product_link',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='state',
            field=models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('inactive', 'Inactive')], default='draft', max_length=25),
        ),
        migrations.AlterField(
            model_name='ad',
            name='title',
            field=models.CharField(default='Title', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ad',
            name='video_file_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='address_1',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='address_2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='alternate_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='pincode',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='brand',
            name='brand_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='company_logo',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_brands', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='brand',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_brands', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(default='Name', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='brand',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='poc',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='signed_contract_doc_file_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='signed_nda_doc_file_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='signed_other_doc_file_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='frequency',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frequency', to='advertisement.Ad'),
        ),
        migrations.AlterField(
            model_name='order',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='advertisement.Product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='advertisement.Brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='link',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='advertisement.ProductCategory'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='name',
            field=models.CharField(default='Name', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productimage',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='advertisement.Product'),
        ),
    ]
