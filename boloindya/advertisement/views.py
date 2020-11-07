# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .models import ProductCategory, Brand, Product
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
import json
import boto3
import time
# Create your views here.
class AdevertisementCallView(TemplateView):
	template_name = 'advertisement/home.html'

@login_required
def brand_onboard_form(request):
	if request.method == 'GET':
		product_categories = ProductCategory.objects.all()
		return render(request,'advertisement/brand/brand_onboard_form.html', {'product_categories': product_categories})
	elif request.method == 'POST':
		print(request.POST)
		# print(request.FILES)
		phone_number = request.POST.get('phone_number',None)
		email = request.POST.get('email',None)
		product_price = request.POST.getlist('product_price',None)
		product_name = request.POST.getlist('product_name',None)
		product_link = request.POST.getlist('product_link',None)
		product_category_id = request.POST.get('product_category',None)
		brand_id = request.POST.get('brand_id',None)
		brand_name = request.POST.get('brand_name',None)
		signed_contract_doc_file = request.FILES.get('signed_contract_doc_file_url',None)
		signed_other_doc_file = request.FILES.get('signed_other_doc_file_url',None)
		signed_nda_doc_file = request.FILES.get('signed_nda_doc_file_url',None)
		company_logo = request.FILES.get('company_logo',None)
		upload_to_bucket = request.POST.get('bucket_name',None)
		brand_folder_key = request.POST.get('folder_prefix','from_upload_panel/advertisement/brand/')
		creator_id = request.user.id

		if not upload_to_bucket:
			return HttpResponse(json.dumps({'message':'fail','reason':'bucket_missing'}),content_type="application/json")
		if not signed_contract_doc_file.name.endswith(('.jpg','.png', '.jpeg')):
			return HttpResponse(json.dumps({'message':'fail','reason':'This is not a jpg/png file'}),content_type="application/json")
		if not signed_other_doc_file.name.endswith(('.jpg','.png', '.jpeg')):
			return HttpResponse(json.dumps({'message':'fail','reason':'This is not a jpg/png file'}),content_type="application/json")
		if not signed_nda_doc_file.name.endswith(('.jpg','.png', '.jpeg')):
			return HttpResponse(json.dumps({'message':'fail','reason':'This is not a jpg/png file'}),content_type="application/json")

		if not company_logo.name.endswith(('.jpg','.png', '.jpeg')):
			return HttpResponse(json.dumps({'message':'fail','reason':'This is not a jpg/png file'}),content_type="application/json")
		
		brand_dict = {}
		if signed_contract_doc_file:
			signed_contract_doc_file_url = upload_media(signed_contract_doc_file, brand_folder_key)
			if not signed_contract_doc_file_url:
				return HttpResponse(json.dumps({'message':'fail','reason':'Failed to upload signed contract file'}),content_type="application/json")
			else:
				brand_dict['signed_contract_doc_file_url'] = signed_contract_doc_file_url

		if signed_other_doc_file:
			signed_other_doc_file_url = upload_media(signed_other_doc_file, brand_folder_key)
			if not signed_other_doc_file_url:
				return HttpResponse(json.dumps({'message':'fail','reason':'Failed to upload signed other doc file'}),content_type="application/json")
			else:
				brand_dict['signed_contract_doc_file_url'] = signed_contract_doc_file_url

		if signed_nda_doc_file:
			signed_nda_doc_file_url = upload_media(signed_nda_doc_file, brand_folder_key)
			if not signed_nda_doc_file_url:
				return HttpResponse(json.dumps({'message':'fail','reason':'Failed to upload signed nda doc file'}),content_type="application/json")
			else:
				brand_dict['signed_nda_doc_file_url'] = signed_nda_doc_file_url

		if company_logo:
			company_logo_url = upload_media(company_logo, brand_folder_key)
			if not company_logo_url:
				return HttpResponse(json.dumps({'message':'fail','reason':'Failed to upload company logo file'}))
			else:
				brand_dict['company_logo'] = company_logo_url

		brand_dict['name'] = brand_name
		brand_dict['email'] = email
		brand_dict['phone_number'] = phone_number
		brand_dict['brand_id'] = brand_id
		brand_dict['product_category_id'] = product_category_id
		brand_dict['created_by_id'] = creator_id
		print(brand_dict)
		brand_obj = Brand.objects.create(**brand_dict)

		#create product
		product_list = []
		# print(product_name, product_link, product_price)
		for name,link,price in zip(product_name, product_link, product_price):
			res = {}
			res['name'] = name
			res['price'] = price
			res['link'] = link
			res['created_by_id'] = creator_id
			res['product_category_id'] = product_category_id
			res['brand_id'] = brand_obj.id
			product_list.append(res)
		# print(product_list)
		product_obj_list = [Product(**vals) for vals in product_list]
		Product.objects.bulk_create(product_obj_list)
		return HttpResponse(json.dumps({'message':'success', 'brand_id':brand_obj.id}),content_type="application/json")

@login_required
def ad_creation_form(request):
	if request.method == 'GET':
		return render(request,'advertisement/ad/new_ad_form.html')
	elif request.method == 'POST':
		print(request.POST)
		print(request.FILES)

@login_required
def product_onboard_form(request):
	if request.method == 'GET':
		return render(request,'advertisement/product/product_onboard_form.html')
	elif request.method == 'POST':
		brand_id = request.POST.get('brand_id',None)
		product_name = request.POST.getlist('product_name',None)
		product_link = request.POST.getlist('product_link',None)
		product_price = request.POST.getlist('product_price',None)
		product_category_id = Brand.objects.get(id=brand_id).product_category_id
		product_list = []
		creator_id = request.user.id
		# print(product_name, product_link, product_price)
		for name,link,price in zip(product_name, product_link, product_price):
			res = {}
			res['name'] = name
			res['price'] = price
			res['link'] = link
			res['created_by_id'] = creator_id
			res['product_category_id'] = product_category_id
			res['brand_id'] =brand_id
			product_list.append(res)
		# print(product_list)
		product_obj_list = [Product(**vals) for vals in product_list]
		Product.objects.bulk_create(product_obj_list)
		return HttpResponse(json.dumps({'message':'success'}),content_type="application/json")

def upload_media(media_file, key="media/"):
    try:
    	from drf_spirit.views import remove_extra_char
        from jarvis.views import urlify
        client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
        ts = time.time()
        created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        media_file_name = remove_extra_char(str(media_file.name))
        filenameNext= media_file_name.split('.')
        final_filename = str(urlify(filenameNext[0]))+"_"+ str(ts).replace(".", "")+"."+str(filenameNext[1])
        client.put_object(Bucket=settings.BOLOINDYA_AWS_IN_BUCKET_NAME, Key=key + final_filename, Body=media_file, ACL='public-read')
        filepath = 'https://s3.ap-south-1.amazonaws.com/' + settings.BOLOINDYA_AWS_IN_BUCKET_NAME + '/'+ key + final_filename
        return filepath
    except Exception as e:
        print(e)
        return None