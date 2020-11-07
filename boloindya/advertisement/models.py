# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class RecordTimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, blank=False, null=False)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    class Meta:
        abstract = True


class ProductCategory(RecordTimeStamp):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Brand(RecordTimeStamp):
    name = models.CharField(max_length=100)
    company_logo = models.CharField(blank=True, null=True, max_length=200)
    brand_id = models.CharField(blank=True, null=True, max_length=20)
    poc = models.CharField(blank=True, null=True, max_length=50)
    phone_number = models.CharField(blank=True, null=True, max_length=20)
    email = models.CharField(blank=True, null=True, max_length=50)
    signed_contract_doc_file_url = models.CharField(blank=True, null=True, max_length=200)
    signed_other_doc_file_url = models.CharField(blank=True, null=True, max_length=200)
    signed_nda_doc_file_url = models.CharField(blank=True, null=True, max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='created_brands')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,related_name='modified_brands')

    def __str__(self):
        return self.name


class Product(RecordTimeStamp):
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    link = models.CharField(blank=True, null=True, max_length=200)
    name = models.CharField(blank=True, null=True, max_length=200)
    product_category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_products')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name = 'modified_products')
    rating_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    currency = models.CharField(max_length=10, default="INR")
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_discounted = models.BooleanField(default=False)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    original_image = models.CharField(blank=True, null=True, max_length=200)
    compressed_image = models.CharField(blank=True, null=True, max_length=200)
    product_id = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)


ad_state_options = (
    ('draft', "Draft"),
    ('active', "Active"),
    ('inactive', "Inactive"),
)

frequency_type_options = (
    ('constant', "Constant"),
    ('variable', "Variable"),
)

class Ad(RecordTimeStamp):
    brand = models.ForeignKey(Brand, related_name='ads', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now=False)
    end_time = models.DateTimeField(auto_now=False)
    product = models.ForeignKey(Product, related_name='ads', on_delete=models.CASCADE)
    ad_type =  models.CharField(max_length=25)
    video_file_url = models.CharField(blank=True, null=True, max_length=200)
    thumbnail = models.CharField(blank=True, null=True, max_length=200)
    ad_length = models.PositiveIntegerField(default=0)
    frequency_type = models.CharField(choices=frequency_type_options, default='constant', max_length=25)
    product_link = models.CharField(blank=True, null=True, max_length=200)
    state = models.CharField(choices=ad_state_options, default='draft', max_length=25)
    budget = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_ads')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='modify_ads')

    def __str__(self):
        return self.title


class Frequency(RecordTimeStamp):
    ad = models.ForeignKey(Ad, related_name='frequency')
    sequence = models.PositiveIntegerField(default=0)
    scroll = models.PositiveIntegerField(default=0)


class Address(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='addresses')
    name = models.CharField(blank=True, null=True, max_length=50)
    phone_number = models.CharField(blank=True, null=True, max_length=20)
    alternate_number = models.CharField(blank=True, null=True, max_length=20)
    email = models.CharField(blank=True, null=True, max_length=50)
    address_1 = models.CharField(blank=True, null =True, max_length=200)
    address_2 = models.CharField(blank=True, null =True, max_length=200)
    city = models.CharField(blank=True, null=True, max_length=50)
    state = models.CharField(blank=True, null=True, max_length=50)
    pincode = models.PositiveIntegerField(blank=True, null = True)


ORDER_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('pending_for_approval', 'Pending for Approval'),
    ('accepted_by_vender', 'Accepted by vendor'),
    ('delivered', 'Delivered')
)

ORDER_PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed')
)


class Order(RecordTimeStamp):
    state = models.CharField(choices=ORDER_STATE_CHOICES, default='draft', max_length=20)
    payment_status = models.CharField(choices=ORDER_PAYMENT_CHOICES, default='pending', max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders')
    shipping_address = models.ForeignKey(Address, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class ProductReview(RecordTimeStamp):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)


class CTA(models.Model):
    ad = models.ForeignKey(Ad, related_name='cta')
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    enable_time = models.PositiveIntegerField(null=True, blank=True)
    action = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title