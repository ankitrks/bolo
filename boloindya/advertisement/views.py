# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
	
from advertisement.models import Ad, ProductReview, Order, Product
from advertisement.serializers import AdSerializer, ReviewSerializer, OrderSerializer, ProductSerializer


class AdDetailAPIView(RetrieveAPIView):
	queryset = Ad.objects.filter(state='active')
	serializer_class = AdSerializer


class ProductDetailAPIView(RetrieveAPIView):
	queryset = Ad.objects.filter(state='active')
	serializer_class = ProductSerializer    

	def get_object(self):
		obj = super(ProductDetailAPIView, self).get_object()
		return obj.product



class ReviewListAPIView(ListAPIView):
	queryset = ProductReview.objects.all()


class OrderListCreateAPIView(ListCreateAPIView):
	queryset = Order.objects.all()

	def get_queryset(self):
		return self.queryset.filter(user=self.request.user)


class CityListAPIView(APIView):
	def get(self, request, *args, **kwargs):
		return {}

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .models import ProductCategory, Brand, Product, Frequency, CTA, ad_type_options
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from rest_framework import status
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
	if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)):
		if request.method == 'GET':
			ad_type_options_values = []
			for value1, value2 in ad_type_options:
				ad_type_options_values.append({'id':value1, 'value':value2})
			print(ad_type_options_values)
			return render(request,'advertisement/ad/new_ad_form.html', {'ad_type_options':ad_type_options_values})
		elif request.method == 'POST':
			try:
				print(request.POST)
				print(request.FILES)
				scrolls = request.POST.getlist('scrolls',None)
				start_date = request.POST.get('start_date',None)
				end_date = request.POST.get('end_date',None)
				title = request.POST.get('title',None)
				toggler = request.POST.get('toggler',None)
				toggler_frequency = request.POST.get('toggler_frequency',None)
				brand_id = request.POST.get('brand_id',None)
				product_id = request.POST.get('product_id',None)
				description = request.POST.get('description',None)
				ad_type = request.POST.get('ad_type',None)
				cta = request.POST.getlist('cta',None)
				is_draft = request.POST.get('is_draft',None)
				ad_video_file = request.FILES.get('video_file',None)
				ad_video_file_link = request.POST.get('video_file_link',None)
				upload_to_bucket = request.POST.get('bucket_name',None)
				ad_folder_key = request.POST.get('folder_prefix','from_upload_panel/advertisement/ad/')
				if all(freq=='' for freq in scrolls):
					return HttpResponse(json.dumps({'message':'fail','reason':'No Frequnecy scroll provided'}),content_type="application/json")
				if not start_date:
					return HttpResponse(json.dumps({'message':'fail','reason':'Invalid Start Date'}),content_type="application/json")
				if toggler=='link' and not ad_video_file_link:
					return HttpResponse(json.dumps({'message':'fail','reason':'Please enter ad video link'}),content_type="application/json")
				if toggler=='upload' and not ad_video_file:
					return HttpResponse(json.dumps({'message':'fail','reason':'Please upload valid ad video file'}),content_type="application/json")
				if toggler=='upload' and not (ad_video_file.name.endswith('.mp4') or ad_video_file.name.endswith('.mov')):
					return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp4  mov file'}),content_type="application/json")
				print("===")
				print(toggler,ad_video_file, ad_video_file_link)



				start_date = datetime.strptime(start_date, "%d-%m-%Y")
				is_draft = True if is_draft=='true' else False
				state = "active"
				if is_draft:
					state = "draft"
				ad_dict = {}
				ad_dict['brand_id'] = brand_id
				ad_dict['title'] = title
				ad_dict['description'] = description
				ad_dict['start_time'] = start_date
				if end_date:
					ad_dict['end_time'] = datetime.strptime(end_date, "%d-%m-%Y")
				if toggler=='link' and ad_video_file_link:
					ad_dict['video_file_url'] = ad_video_file_link
				ad_dict['frequency_type'] = toggler_frequency
				ad_dict['created_by_id'] = request.user.id
				ad_dict['product_id'] = product_id
				ad_dict['state'] = state
				if ad_video_file:
					ad_folder_key_url = upload_media(ad_video_file, ad_folder_key)
					if not ad_folder_key_url:
						return HttpResponse(json.dumps({'message':'fail','reason':'Failed to upload signed contract file'}),content_type="application/json")
					else:
						ad_dict['video_file_url'] = ad_folder_key_url
				ad_obj = Ad.objects.create(**ad_dict)

				scrolls = list(filter(bool,scrolls))
				#create frequency objects
				for index,value in enumerate(scrolls):
					if value:
						Frequency(ad_id=ad_obj.id,sequence=index+1,scroll=value).save()
				#add cta
				for value in cta:
					CTA(ad_id=ad_obj.id, title=value).save()

				return HttpResponse(json.dumps({'message':'success', 'ad_id':ad_obj.id}),content_type="application/json")
			except Exception as e:
				return HttpResponse(json.dumps({'message':'fail','reason':str(e)}),content_type="application/json")


	else:
		return HttpResponse(json.dumps({'message':'fail','reason':'Not Authorised'}),content_type="application/json")

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

@login_required
def search_fields_for_advertisement(request):
	raw_data = json.loads(request.body)
	query = raw_data['query']
	result_type = raw_data['result_type']
	try:
		if result_type == '0':
			data = list(Brand.objects.filter(name__istartswith=query).values('id','name'))
			return JsonResponse({'data': data}, status=status.HTTP_200_OK )
		elif result_type == '1':
			data = list(Product.objects.filter(name__istartswith=query).values('id','name'))
			return JsonResponse({'data': data}, status=status.HTTP_200_OK )
	except Exception as e:
		print(e)
		return JsonResponse({'data': [], 'error': str(e)}, status=status.HTTP_200_OK)