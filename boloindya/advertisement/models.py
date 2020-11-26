# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.search import  SearchVectorField

from dynamodb_api import create as dynamodb_create


""" DynamoDB models """
AdEvent = 'AdEvent_%s'%settings.DYNAMODB_ENV
Counter = 'Counter_%s'%settings.DYNAMODB_ENV
Event = 'Event_%s'%settings.DYNAMODB_ENV


""" RDS Models """

class PermissionManager(models.Manager):
    def for_brand_user(self, brand_user):
        return super(PermissionManager, self).get_queryset().filter(lines__product__brand=brand_user.brand)


class EventLogManager(models.Manager):
    def update(self, **kwargs):
        print 'in update', kwargs
        print '__  data ', self.__dict__
        return super(EventLogManager, self).update(**kwargs)


class ModelRemastered(models.Model):
    class Meta:
        abstract = True

    def save(self, **kwargs):
        if kwargs.get('user'):
            request = kwargs.pop('user')

        event = 'UPDATE_%s'

        if not self.id:
            event = 'CREATE_%s'

        instance = super(ModelRemastered, self).save(**kwargs)

        dynamodb_create(Event, {
            'event': event%self.__class__.__name__.upper(),
            'id': instance.id,
            'table': instance._meta.db_table
        })



class RecordTimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, blank=False, null=False)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    objects = EventLogManager()

    class Meta:
        abstract = True


class ProductCategory(RecordTimeStamp):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Brand(RecordTimeStamp):
    name = models.CharField(max_length=100)
    company_logo = models.CharField(blank=True, null=True, max_length=200)
    brand_id = models.CharField(blank=True, null=True, max_length=20)
    poc = models.CharField(blank=True, null=True, max_length=50)
    poc_user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='brand')
    phone_number = models.CharField(blank=True, null=True, max_length=20)
    email = models.CharField(blank=True, null=True, max_length=50)
    signed_contract_doc_file_url = models.CharField(blank=True, null=True, max_length=200)
    signed_other_doc_file_url = models.CharField(blank=True, null=True, max_length=200)
    signed_nda_doc_file_url = models.CharField(blank=True, null=True, max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='created_brands')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,related_name='modified_brands')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def clean(self):
        if Brand.objects.filter(name__iexact=self.name):
            raise ValidationError({
                'name': [
                    ValidationError(
                        message=_("Already Brand Exist with same name"),
                        code='invalid',
                        params={},
                    )
                ]
            })
            super(Brand, self).clean()


class Tax(models.Model):
    name = models.CharField(max_length=20)
    percentage = models.FloatField()

    def __unicode__(self):
        return "%s = %s"%(self.name, self.percentage)

    def get_value(self, base_amount):
        return (self.percentage * float(base_amount)) / 100.0


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
    discount_expiry = models.DateTimeField(blank=True, null=True)
    max_quantity_limit = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    taxes = models.ManyToManyField(Tax)

    def __str__(self):
        return self.name

    @property
    def final_amount(self):
        if self.is_discounted:
            return float(self.discounted_price)
        return float(self.mrp)

    @property
    def base_amount(self):
        amount = float(self.final_amount)

        if not self.taxes:
            return round(amount, 2)
        
        return round(amount / sum([1] + [tax.percentage/100.0 for tax in self.taxes.all()]), 2)

    @property
    def amount_including_tax(self):
        return float(self.final_amount) + float(self.total_tax)

    @property
    def total_tax(self):
        base_amount = self.final_amount
        return sum([base_amount * float(tax.percentage)/100.0 for tax in self.taxes.all()])


    def get_tax_value(self, percentage):
        return round(float(self.final_amount) * percentage / 100.0, 2)


class ProductImage(models.Model):
    original_image = models.CharField(blank=True, null=True, max_length=200)
    compressed_image = models.CharField(blank=True, null=True, max_length=200)
    product_id = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)


ad_state_options = (
    ('draft', "Draft"),
    ('active', "Active"),
    ('inactive', "Inactive"),
    ('deleted', "Deleted"),
    ('ongoing', "Ongoing"),
    ('completed', "Completed"),
)

frequency_type_options = (
    ('constant', "Constant"),
    ('variable', "Variable"),
)

AD_TYPE_CHOICES = (
    ('install_now', 'Install Now'),
    ('shop_now', 'Shop Now'),
    ('learn_more','Learn More')
)

class Ad(RecordTimeStamp):
    brand = models.ForeignKey(Brand, related_name='ads', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now=False)
    end_time = models.DateTimeField(auto_now=False, null=True)
    product = models.ForeignKey(Product, related_name='ads', on_delete=models.CASCADE, null=True)
    ad_type =  models.CharField(max_length=25, choices=AD_TYPE_CHOICES, default='shop_now')
    video_file_url = models.CharField(blank=True, null=True, max_length=200)
    thumbnail = models.CharField(blank=True, null=True, max_length=200)
    ad_length = models.PositiveIntegerField(default=0)
    frequency_type = models.CharField(choices=frequency_type_options, default='constant', max_length=25)
    product_link = models.CharField(blank=True, null=True, max_length=200)
    state = models.CharField(choices=ad_state_options, default='draft', max_length=25)
    budget = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_ads')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='modify_ads')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Frequency(RecordTimeStamp):
    ad = models.ForeignKey(Ad, related_name='frequency')
    sequence = models.PositiveIntegerField(default=0)
    scroll = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        if self.ad.frequency_type == 'constant':
            return '%s at every %s scrolls'%(self.ad, self.scroll)
        elif self.ad.frequency_type == 'variable':
            return '%s after %s scrolls'%(self.ad, self.scroll)


class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, related_name='cities')

    def __str__(self):
        return self.name


class Address(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='addresses')
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20)
    alternate_number = models.CharField(blank=True, null=True, max_length=20)
    email = models.CharField(blank=True, null=True, max_length=50)
    address1 = models.CharField(blank=True, null =True, max_length=200)
    address2 = models.CharField(blank=True, null =True, max_length=200)
    address3 = models.CharField(blank=True, null =True, max_length=200)
    city = models.ForeignKey(City, related_name='addresses')
    state = models.ForeignKey(State, related_name='addresses')
    pincode = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)


ORDER_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('order_placed', 'Order Placed'),
    ('shipped', 'Shipped'),
    ('out_of_stock', 'Out of Stock'),
    ('returned', 'Returned'),
    ('delivered', 'Delivered'),
    ('pending_for_approval', 'Pending for Approval'), 
    ('accepted_by_vender', 'Accepted by vendor')
)

ORDER_PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('initiated', 'Initiated'),
    ('success', 'Success'),
    ('failed', 'Failed')
)

PAYMENT_METHOD_CHOICES = (
    ('card', 'Card'),
)


class Order(RecordTimeStamp):
    state = models.CharField(choices=ORDER_STATE_CHOICES, default='draft', max_length=20)
    payment_status = models.CharField(choices=ORDER_PAYMENT_CHOICES, default='pending', max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders')
    shipping_address = models.ForeignKey(Address, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_gateway_order_id = models.CharField(max_length=30, null=True, blank=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=20, null=True, blank=True)
    order_number = models.CharField(max_length=30, null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    body_text = SearchVectorField(null=True, blank=True)

    objects = PermissionManager()

    @property
    def amount_including_tax(self):
        return sum([line.product.amount_including_tax * line.quantity for line in self.lines.all()])

class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name='lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_lines', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)


class ProductReview(RecordTimeStamp):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)

class CTA(models.Model):
    ad = models.ForeignKey(Ad, related_name='cta')
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    enable_time = models.PositiveIntegerField(null=True, blank=True)
    action = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title


class AdEventAbstract(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s')
    ad = models.ForeignKey(Brand, related_name='%(class)s', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Seen(AdEventAbstract):
    pass

class Skipped(AdEventAbstract):
    pass


class Clicked(AdEventAbstract):
    cta = models.CharField(max_length=50, null=True, blank=True)


class Playtime(AdEventAbstract):
    playtime = models.PositiveIntegerField(default=0)


class Install(AdEventAbstract):
    pass

class ShopNow(AdEventAbstract):
    pass

class LearnMore(AdEventAbstract):
    pass

class PlaceOrder(AdEventAbstract):
    pass
