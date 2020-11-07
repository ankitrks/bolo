# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from forum.topic.models import RecordTimeStamp

# Create your models here.
class ProductCategory(RecordTimeStamp):
	name = models.TextField(blank = True, null = True)

class Brand(RecordTimeStamp):
	name = models.TextField(blank = True, null = True)
	company_logo = models.TextField(blank = True, null = True)
	brand_id = models.TextField(blank = True, null = True)
	product_category = models.ForeignKey(ProductCategory, related_name='product_category_brand', on_delete=models.CASCADE)
	poc = models.TextField(blank = True, null = True)
	phone_number = models.TextField(blank = True, null = True)
	email = models.TextField(blank = True, null = True)
	signed_contract_doc_file_url = models.TextField(blank = True, null = True)
	signed_other_doc_file_url = models.TextField(blank = True, null = True)
	signed_nda_doc_file_url = models.TextField(blank = True, null = True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='as_brand_creator')
	last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True,related_name='as_brand_modifier')

class Product(RecordTimeStamp):
	brand = models.ForeignKey(Brand, related_name='brand_product', on_delete=models.CASCADE)
	link = models.TextField(blank = True, null = True)
	name = models.TextField(blank = True, null = True)
	price = models.DecimalField(max_digits = 10, decimal_places = 2,default=0.0)
	product_category = models.ForeignKey(ProductCategory, related_name='product_category_product', on_delete=models.CASCADE)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='as_product_creator')
	last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name = 'as_product_modifier')

ad_state_options = (
	('draft', "Draft"),
	('active', "Active"),
	('inactive', "Inactive"),
	)
frequency_type_options = (
	('constant', "Constant"),
	('variable', "Variable"),)
class Ad(RecordTimeStamp):
	brand = models.ForeignKey(Brand, related_name='brand_ad', on_delete=models.CASCADE)
	title = models.TextField(blank = True, null = True)
	description = models.TextField(blank = True, null = True)
	start_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	end_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	product = models.ForeignKey(Product, related_name='product_ad', on_delete=models.CASCADE)
	ad_type =  models.CharField(max_length = 25)
	video_file_url = models.TextField(blank = True, null = True)
	frequency_type = models.CharField(choices = frequency_type_options,default='constant', blank = True, null = True, max_length = 25)
	product_link = models.TextField(blank = True, null = True)
	state = models.CharField(choices = ad_state_options,default='draft', blank = True, null = True, max_length = 25)
	budget = models.PositiveIntegerField(default=0)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='as_ad_creator')
	last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='as_ad_modifier')

class Frequency(RecordTimeStamp):
	ad = models.ForeignKey(Ad, related_name='ad_frequency')
	sequence = models.PositiveIntegerField(default=0)
	scroll = models.PositiveIntegerField(default=0)

class Address(RecordTimeStamp):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_brand_ad_address')
	name = models.TextField(blank = True, null = True)
	phone_number = models.TextField(blank = True, null = True)
	alternate_number = models.TextField(blank = True, null = True)
	email = models.TextField(blank = True, null = True)
	address_1 = models.TextField(blank = True, null =True)
	address_2 = models.TextField(blank = True, null =True)
	city = models.TextField(blank = True, null = True)
	state = models.TextField(blank = True, null = True)
	pincode = models.TextField(blank = True, null = True)

class Order(RecordTimeStamp):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_brand_ad_order')
	shipping_address_id = models.ForeignKey(Address,related_name='address_order')
	date = models.DateTimeField(auto_now=False, blank=False, null=False)
	amount = models.DecimalField(max_digits = 10, decimal_places = 2,default=0.0)
	product = models.ForeignKey(Product, related_name='product_order', on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=0)