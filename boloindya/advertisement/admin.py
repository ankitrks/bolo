# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import nested_admin

from django import forms
from .views import upload_media
from advertisement.models import *
import boto3
from string import Template
from django.utils.safestring import mark_safe

class CompanyLogoWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        if value:
            html =  Template("""<div>
                <input type="file" name="company_logo" id="id_company_logo" class="form-control">
                <img src="$link" width="100" height="100"/>
                </div>""")
            return mark_safe(html.substitute(link=value))
        else:
            html =  Template("""
                <input type="file" name="company_logo" id="id_company_logo">
                """)
            return mark_safe(html.substitute(link=value))

class SignedContractDocFileWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        if value:
            html =  Template("""<div>
                <input type="file" name="signed_contract_doc_file_url" id="id_signed_contract_doc_file_url" class="form-control">
                <img src="$link" width="100" height="100"/>
                </div>""")
            return mark_safe(html.substitute(link=value))
        else:
            html =  Template("""<div>
                <input type="file" name="signed_contract_doc_file_url" id="id_signed_contract_doc_file_url" class="form-control">
                </div>""")
            return mark_safe(html.substitute(link=value))

class SignedOtherDocFileWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        if value:
            html =  Template("""<div>
                <input type="file" name="signed_other_doc_file_url" id="id_signed_other_doc_file_url" class="form-control">
                <img src="$link" width="100" height="100"/>
                </div>""")
            return mark_safe(html.substitute(link=value))
        else:
            html =  Template("""<div>
                <input type="file" name="signed_other_doc_file_url" id="id_signed_other_doc_file_url" class="form-control">
                </div>""")
            return mark_safe(html.substitute(link=value))

class SignedNdaDocFileWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        if value:
            html =  Template("""<div>
                <input type="file" name="signed_nda_doc_file_url" id="id_signed_nda_doc_file_url" class="form-control">
                <img src="$link" width="100" height="100"/>
                </div>""")
            return mark_safe(html.substitute(link=value))
        else:
            html =  Template("""<div>
                <input type="file" name="signed_nda_doc_file_url" id="id_signed_nda_doc_file_url" class="form-control">
                </div>""")
            return mark_safe(html.substitute(link=value))

class ProductImageWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        if value:
            html =  Template("""<div>
                <input type="file" name="original_image" id="id_original_image" class="form-control">
                <img src="$link" width="100" height="100"/>
                </div>""")
            return mark_safe(html.substitute(link=value))
        else:
            html =  Template("""<div>
                <input type="file" name="original_image" id="id_original_image" class="form-control">
                </div>""")
            return mark_safe(html.substitute(link=value))

class ProductImageFields(forms.ModelForm):
    file_image = forms.FileField(required=False)

    class Meta:
        model = ProductImage
        fields = ('original_image',)

class ProductReviewInline(nested_admin.NestedStackedInline):
    model = ProductReview
    fields = ('title','description','rating')
    extra = 0

class ProductImageInline(nested_admin.NestedStackedInline):
    model = ProductImage
    form = ProductImageFields
    fields = ('file_image','original_image',)
    readonly_fields = ('original_image',)
    extra = 0

class ProductInline(nested_admin.NestedStackedInline):
    model = Product
    fields = ('name','link','product_category','mrp','description','rating')
    inlines = [ProductReviewInline, ProductImageInline]
    extra = 0


class BrandInline(admin.TabularInline):
    model = Brand

class BrandExtraFieldsForm(forms.ModelForm):
    company_logo = forms.FileField(widget=CompanyLogoWidget, required=False)
    signed_contract_doc_file_url = forms.FileField(widget=SignedContractDocFileWidget, required=False)
    signed_other_doc_file_url = forms.FileField(widget=SignedOtherDocFileWidget, required=False)
    signed_nda_doc_file_url = forms.FileField(widget=SignedNdaDocFileWidget, required=False)
    class Meta:
        fields = ('name','poc','phone_number','email','is_active')
        model = Brand

class BrandAdmin(nested_admin.NestedModelAdmin):
    form = BrandExtraFieldsForm
    list_display = ('name','brand_id','poc','phone_number','email','is_active')
    inlines = [ProductInline]

    def __init__(self, *args, **kwargs):
        self.s3_client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        super(BrandAdmin,self).__init__(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        input_data = form.cleaned_data
        company_logo = request.FILES.get('company_logo',None)
        signed_nda_doc_file_url = request.FILES.get('signed_nda_doc_file_url',None)
        signed_contract_doc_file_url = request.FILES.get('signed_contract_doc_file_url',None)
        signed_other_doc_file_url = request.FILES.get('signed_other_doc_file_url',None)
        brand_folder_key = 'from_upload_panel/advertisement/brand/'
        obj.phone_number = input_data['phone_number']
        obj.name = input_data['name']
        obj.email = input_data['email']
        obj.poc = input_data['poc']
        obj.is_active = input_data['is_active']
        if company_logo:
            obj.company_logo = upload_media(self.s3_client, company_logo,brand_folder_key)
        if signed_nda_doc_file_url:
            obj.signed_nda_doc_file_url = upload_media(self.s3_client, signed_nda_doc_file_url, brand_folder_key)
        if signed_other_doc_file_url:
            obj.signed_other_doc_file_url = upload_media(self.s3_client, signed_other_doc_file_url, brand_folder_key)
        if signed_contract_doc_file_url:
            obj.signed_contract_doc_file_url = upload_media(self.s3_client,signed_contract_doc_file_url, brand_folder_key)
        obj.created_by_id = request.user.id
        obj.save()
        super(BrandAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        product_images_folder_prefix = 'from_upload_panel/advertisement/product/'
        for formset in formsets:
            instances = formset.save(commit=False)
            #this is because in product image we have image as extra field
            print(instances,formset.cleaned_data)
            if any([isinstance(obj, ProductImage) for obj in instances]):
                cleaned_dataset = formset.cleaned_data
                cleaned_dataset = list(filter(lambda obj: obj and obj['file_image'], cleaned_dataset))
                for (cleaned_data,instance) in zip(cleaned_dataset, instances):
                    if cleaned_data:
                        instance.product_id = cleaned_data['product_id']
                        instance.original_image = upload_media(self.s3_client,cleaned_data['file_image'], product_images_folder_prefix)
                        instance.save()
            for instance in instances:
                if isinstance(instance, ProductImage):
                    continue
                elif isinstance(instance, Product):
                    instance.created_by_id = request.user.id
                    instance.save()
                    tax = Tax.objects.first()
                    instance.taxes.add(tax)
                else:
                    instance.save()

        super(BrandAdmin, self).save_related(request, form, formsets, change)

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
        input_data = form.cleaned_data
        obj.name = input_data['name']
        obj.product_category = input_data['product_category']
        obj.brand = input_data['brand']
        obj.mrp = input_data['mrp']
        obj.link = input_data['link']
        obj.description = input_data['description']
        obj.created_by_id = request.user.id
        obj.save()
        tax = Tax.objects.first()
        obj.taxes.add(tax)
        super(ProductAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        product_images_folder_prefix = 'from_upload_panel/advertisement/product/'
        for formset in formsets:
            instances = formset.save(commit=False)
            print(instances, formset.cleaned_data)
            if any([isinstance(obj, ProductImage) for obj in instances]):
                cleaned_dataset = formset.cleaned_data
                cleaned_dataset = list(filter(lambda obj: obj and obj['file_image'], cleaned_dataset))
                for (cleaned_data,instance) in zip(cleaned_dataset, instances):
                    if cleaned_data and cleaned_data['file_image']:
                        instance.product_id = cleaned_data['product_id']
                        instance.original_image = upload_media(self.s3_client,cleaned_data['file_image'], product_images_folder_prefix)
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
admin.site.register(Tax)
