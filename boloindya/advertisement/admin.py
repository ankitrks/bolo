# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import nested_admin

from django import forms
from .views import upload_media
from advertisement.models import *
import boto3


class ProductImageFields(forms.ModelForm):
    original_image = forms.FileField()

class ProductReviewInline(nested_admin.NestedStackedInline):
    model = ProductReview
    fields = ('title','description','rating')

class ProductImageInline(nested_admin.NestedStackedInline):
    model = ProductImage
    form = ProductImageFields
    fields = ('original_image',)

class ProductInline(nested_admin.NestedStackedInline):
    model = Product
    fields = ('name','link','product_category','mrp','description','rating')
    inlines = [ProductReviewInline, ProductImageInline]


class BrandInline(admin.TabularInline):
    model = Brand

class BrandExtraFieldsForm(forms.ModelForm):
    company_logo = forms.FileField()
    signed_contract_doc_file_url = forms.FileField()
    signed_other_doc_file_url = forms.FileField()
    signed_nda_doc_file_url = forms.FileField()
    class Meta:
        fields = ('name','poc','phone_number','email','is_active')
        model = Brand

class BrandAdmin(nested_admin.NestedModelAdmin):
    form = BrandExtraFieldsForm
    list_display = ('name','company_logo','brand_id','poc','phone_number','email','signed_contract_doc_file_url','signed_other_doc_file_url','signed_nda_doc_file_url','is_active')
    inlines = [ProductInline]

    def __init__(self, *args, **kwargs):
        self.s3_client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        super(BrandAdmin,self).__init__(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            input_data = form.cleaned_data
            brand_folder_key = 'from_upload_panel/advertisement/brand/'
            obj.phone_number = input_data['phone_number']
            obj.name = input_data['name']
            obj.email = input_data['email']
            obj.poc = input_data['poc']
            obj.is_active = input_data['is_active']
            obj.company_logo = upload_media(self.s3_client, input_data['company_logo'],brand_folder_key)
            obj.signed_nda_doc_file_url = upload_media(self.s3_client, input_data['signed_nda_doc_file_url'], brand_folder_key)
            obj.signed_other_doc_file_url = upload_media(self.s3_client, input_data['signed_other_doc_file_url'], brand_folder_key)
            obj.signed_contract_doc_file_url = upload_media(self.s3_client,input_data['signed_contract_doc_file_url'], brand_folder_key)
            obj.created_by_id = request.user.id
            obj.save()
            super(BrandAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        product_images_folder_prefix = 'from_upload_panel/advertisement/product/'
        for formset in formsets:
            instances = formset.save(commit=False)
            #this is because in product image we have image as extra field
            if any([isinstance(obj, ProductImage) for obj in instances]):
                for (cleaned_data,instance) in zip(formset.cleaned_data, instances):
                    if cleaned_data:
                        instance.product_id = cleaned_data['product_id']
                        instance.original_image = upload_media(self.s3_client,cleaned_data['original_image'], product_images_folder_prefix)
                        instance.save()
            for instance in instances:
                if isinstance(instance, ProductImage):
                    continue
                elif isinstance(instance, Product):
                    instance.created_by_id = request.user.id
                instance.save()

        super(BrandAdmin, self).save_related(request, form, formsets, change)


# class AdAdmin(admin.ModelAdmin):
#     list_display = ('brand', 'title', 'description', 'start_time','end_time','product','ad_type','video_file_url','ad_length','thumbnail','frequency_type','product_link','state','budget')
#     fields = ('brand', 'title', 'description', 'start_time','end_time','product','ad_type','video_file_url','ad_length','thumbnail','frequency_type','product_link','state','budget')
#     inlines = [BrandInline,ProductInline]
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('brand','name', 'link','product_category','mrp','description', 'rating',)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ('link', 'name', 'brand')
    inlines = [ProductReviewInline, ProductImageInline]
    form = ProductForm

    def __init__(self, *args, **kwargs):
        self.s3_client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        super(ProductAdmin,self).__init__(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            input_data = form.cleaned_data
            obj.name = input_data['name']
            obj.product_category = input_data['product_category']
            obj.brand = input_data['brand']
            obj.mrp = input_data['mrp']
            obj.link = input_data['link']
            obj.description = input_data['description']
            obj.created_by_id = request.user.id
            obj.save()
            super(ProductAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        product_images_folder_prefix = 'from_upload_panel/advertisement/product/'
        for formset in formsets:
            instances = formset.save(commit=False)
            print(instances, formset.cleaned_data)
            if any([isinstance(obj, ProductImage) for obj in instances]):
                for (cleaned_data,instance) in zip(formset.cleaned_data, instances):
                    if cleaned_data:
                        instance.product_id = cleaned_data['product_id']
                        instance.original_image = upload_media(self.s3_client,cleaned_data['original_image'], product_images_folder_prefix)
                        instance.save()
            for instance in instances:
                if isinstance(instance, ProductImage):
                    continue
                instance.save()

admin.site.register(ProductCategory)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Ad)
admin.site.register(Frequency)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(ProductReview)
admin.site.register(CTA)
admin.site.register(OrderLine)