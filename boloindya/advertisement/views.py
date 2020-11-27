# # -*- coding: utf-8 -*-
from __future__ import unicode_literals
from copy import deepcopy
from datetime import datetime, timedelta
from multiprocessing import Process, Pool, Manager, Lock

from django.shortcuts import render
from django.db.models import Sum, Q
from django.test import Client
from django.views.generic import RedirectView, TemplateView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.db import connections
from django.db.models.functions import Lower


from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.pagination import PageNumberPagination

from dynamodb_api import create as dynamodb_create
from redis_utils import get_redis, redis_cli, redis_cli_read_only
from payment.razorpay import create_order
from drf_spirit.models import DatabaseRecordCount

from advertisement.utils import query_fetch_data, convert_to_dict_format, filter_data_from_dict, PageNumberPaginationRemastered
from advertisement.models import (Ad, ProductReview, Order, Product, Address, OrderLine, AdEvent,
                                    Seen, Skipped, Clicked, Brand)
from advertisement.serializers import (AdSerializer, ReviewSerializer, OrderSerializer, ProductSerializer, AddressSerializer, 
                                        OrderCreateSerializer, OrderLineSerializer, ChangePasswordSerializer)
from drf_spirit.utils import language_options


class AdDetailAPIView(RetrieveAPIView):
    queryset = Ad.objects.filter(is_deleted=False)
    serializer_class = AdSerializer


class ProductDetailAPIView(RetrieveAPIView):
    queryset = Ad.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer    

    def get_object(self):
        obj = super(ProductDetailAPIView, self).get_object()
        return obj.product


class JarvisAdViewset(ModelViewSet):
    queryset = Ad.objects.filter(is_deleted=False)
    serializer_class = AdSerializer
    pagination_class = deepcopy(PageNumberPaginationRemastered)
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        page_size = self.request.query_params.get('page_size')
        brand_name = self.request.query_params.get('brand_name')
        product_name = self.request.query_params.get('product_name')
        section = self.request.query_params.get('section')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if q:
            try:
                q = int(q)
                queryset = queryset.filter(Q(product_id=q) | Q(brand_id=q))
            except Exception as e:
                queryset = queryset.filter(Q(product__name__icontains=q) | Q(brand__name__icontains=q))
        if brand_name:
            queryset = queryset.filter(brand__name__icontains=brand_name)
        if product_name:
            queryset = queryset.filter(product__name__icontains=product_name)
        
        if section:
            if section == 'ongoing':
                queryset = queryset.filter(state='ongoing')
            elif section == 'upcoming':
                queryset = queryset.filter(state='active')
            elif section == 'history':
                queryset = queryset.filter(state='completed')
            elif section == 'draft':
                queryset = queryset.filter(state='draft')

        if start_date:
            queryset = queryset.filter(start_time__date__gte=datetime.strptime(start_date, '%d-%m-%Y'))
        if end_date:
            queryset = queryset.filter(end_time__date__lte=datetime.strptime(end_date, '%d-%m-%Y'))
            

        if page_size:
            self.pagination_class.page_size = int(page_size)

        return queryset.order_by('id')


class JarvisOrderViewset(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = deepcopy(PageNumberPaginationRemastered)
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        queryset = self.queryset.exclude(state='draft')
        q = self.request.query_params.get('q')
        page_size = self.request.query_params.get('page_size')
        order_date = self.request.query_params.get('date')
        section = self.request.query_params.get('section')
        payment_status = self.request.query_params.get('payment_status')
        amount_range = self.request.query_params.get('amount_range')
        product_ids = self.request.query_params.get('product_ids')
        product_sort = self.request.query_params.get('product_sort')

        if q:
            queryset = queryset.filter(Q(shipping_address__name__icontains=q) | Q(shipping_address__mobile__icontains=q) | 
                                        Q(shipping_address__email__icontains=q))

        if order_date:
            print "order date", order_date
            start_date, end_date = order_date.split(' - ')
            queryset = queryset.filter(date__date__gte=datetime.strptime(start_date, '%d-%m-%Y'), date__date__lte=datetime.strptime(end_date, '%d-%m-%Y'))

        if amount_range:
            print 'amount range', amount_range
            min_amount, max_amount = amount_range.split(' - ')
            queryset = queryset.filter(amount__gte=float(min_amount), amount__lte=float(max_amount))
            query = queryset.query.sql_with_params()
            print 'query', query[0]%query[1]

        if payment_status:
            queryset = queryset.filter(payment_status__in=payment_status.split(','))

        if product_ids:
            queryset = queryset.filter(lines__product_id__in=product_ids.split(','))

        if page_size:
            self.pagination_class.page_size = int(page_size)

        if product_sort:
            if product_sort == 'asc':
                queryset = queryset.order_by(Lower('lines__product_id__name'))
            elif product_sort == 'desc':
                queryset = queryset.order_by(Lower('lines__product_id__name').desc())
        else:
            queryset.order_by('-id')

        return queryset 

class JarvisProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = deepcopy(PageNumberPaginationRemastered)
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        page_size = self.request.query_params.get('page_size')

        if q:
            try:
                q = int(q)
                queryset = queryset.filter(Q(id=q) | Q(brand_id=q))
            except Exception as e:
                queryset = queryset.filter(Q(name__icontains=q) | Q(brand__name__icontains=q))


        # if order_date:
        #     queryset = queryset.filter(date__date=order_date)

        if page_size:
            self.pagination_class.page_size = int(page_size)

        return queryset.order_by('id')


class ReviewListAPIView(ListAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        if self.request.parser_context.get('kwargs', {}).get('product_id'):
            return self.queryset.filter(product_id=self.request.parser_context.get('kwargs', {}).get('product_id'))

        return []


# class OrderListCreateAPIView(ListCreateAPIView):
#     queryset = Order.objects.all()
#     queryset = ProductReview.objects.all()
#     serializer_class = ReviewSerializer
#     pagination_class = PageNumberPagination

#     def get_queryset(self):
#         product_id = self.request.parser_context.get('kwargs', {}).get('product_id')
#         return self.queryset.filter(product_id=product_id)


class AddressViewset(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderViewset(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        client = APIClient()
        request_data = deepcopy(request.data)
        request_meta = request.META

        """ Saving Address """
        address_data = filter_data_from_dict(['name', 'mobile', 'address1', 'address2', 'address3', 'city_id', 'state_id', 'pincode', 'email'], request.data)
        address_data['state'] = address_data.pop('state_id', '')
        address_data['city'] = address_data.pop('city_id', '')
        # address = client.post('/api/v1/ad/address/', address_data, HTTP_AUTHORIZATION=request_meta.get('HTTP_AUTHORIZATION')).json()
        # print "Address", address

        """ Saving Order """
        product_data = filter_data_from_dict(['product_id', 'quantity'], request.data)
        order_data = {
            'amount': 0.0,
            'lines': [{
                'product': product_data.get('product_id'),
                'quantity': product_data.get('quantity')
            }],
            'shipping_address': address_data
        }

        if request_data.get('order_id'):
            order_id = request_data.get('order_id')

            if type(order_id) == list:
                order_id = order_id[0]

            response = client.patch('/api/v1/ad/order/%s/'%order_id, order_data, HTTP_AUTHORIZATION=request_meta.get('HTTP_AUTHORIZATION'), format='json')
        else:
            response = client.post('/api/v1/ad/order/', order_data, HTTP_AUTHORIZATION=request_meta.get('HTTP_AUTHORIZATION'), format='json')
        return Response(response.json(), status=response.status_code)



class CityListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        state = {}

        for row in query_fetch_data("""
                        select state.id as state_id, state.name as state, city.id as city_id, city.name as city
                        from advertisement_city city
                        inner join advertisement_state state on state.id = city.state_id
                    """):
            state_id = row.get('state_id')
            if not state.get(state_id):
                state[state_id] = {
                    'state_id': state_id,
                    'state': row.get('state'),
                    'cities': [{
                        'city': row.get('city'),
                        'city_id': row.get('city_id')
                    }]
                }
            else:
                state[state_id]['cities'].append({
                    'city': row.get('city'),
                    'city_id': row.get('city_id')
                })

        return Response({'results': state.values()}, status=200)

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .models import ProductCategory, Brand, Product, Frequency, CTA, AD_TYPE_CHOICES as ad_type_options
from .utils import CTA_OPTIONS
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
            cta_options_values = []
            for value1, value2 in CTA_OPTIONS.items():
                if value1!='skip':
                    cta_options_values.append({'id':value1, 'value':value2})
            for value1, value2 in ad_type_options:
                ad_type_options_values.append({'id':value1, 'value':value2})
            lang_options = []
            for id_,value in language_options:
                lang_options.append({'id':id_, 'value':value})
            return render(request,'advertisement/ad/new_ad_form.html', {'ad_type_options':ad_type_options_values,'cta_options': cta_options_values, 'lang_options': lang_options})
        elif request.method == 'POST':
            try:
                print(request.POST)
                s3_client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
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
                cta_type_1 = request.POST.get('cta_type_1',None)
                cta_type_2 = request.POST.get('cta_type_2',None)
                cta_type_1_text = request.POST.get('cta_type_1_text',None)
                is_draft = request.POST.get('is_draft',None)
                ad_video_file = request.FILES.get('video_file',None)
                ad_video_file_link = request.POST.get('video_file_link',None)
                upload_to_bucket = request.POST.get('bucket_name',None)
                mrp = request.POST.get('mrp',None)
                discount = request.POST.get('discount',None)
                playstore_link = request.POST.get('playstore_link', None)
                website_link = request.POST.get('website_link', None)
                ad_id = request.POST.get('ad_id', None)
                languages = request.POST.getlist('lang_options',None)
                ad_folder_key = request.POST.get('folder_prefix','from_upload_panel/advertisement/ad/')
                if all(freq=='' for freq in scrolls):
                    return HttpResponse(json.dumps({'message':'fail','reason':'No Frequnecy scroll provided'}),content_type="application/json")
                if not start_date:
                    return HttpResponse(json.dumps({'message':'fail','reason':'Invalid Start Date'}),content_type="application/json")
                if toggler=='link' and not ad_video_file_link:
                    return HttpResponse(json.dumps({'message':'fail','reason':'Please enter ad video link'}),content_type="application/json")
                if toggler=='upload':
                    if not ad_id:
                        if not ad_video_file:
                            return HttpResponse(json.dumps({'message':'fail','reason':'Please upload valid ad video file'}),content_type="application/json")
                        if not (ad_video_file.name.endswith('.mp4') or ad_video_file.name.endswith('.mov')):
                            return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp4  mov file'}),content_type="application/json")
                    else:
                        if ad_video_file and not (ad_video_file.name.endswith('.mp4') or ad_video_file.name.endswith('.mov')):
                            return HttpResponse(json.dumps({'message':'fail','reason':'This is not a mp4  mov file'}),content_type="application/json")
                if mrp and discount and float(mrp)<float(discount):
                    return HttpResponse(json.dumps({'message':'fail','reason':'Discount can not be more than mrp'}),content_type="application/json")

                if not languages:
                    return HttpResponse(json.dumps({'message':'fail','reason':'Please select atleast one language'}),content_type="application/json")

                start_date = datetime.strptime(start_date, "%m/%d/%Y %I:%M %p")
                is_draft = True if is_draft=='true' else False
                state = None
                if is_draft:
                    state = "draft"
                ad_dict = {}
                ad_dict['brand_id'] = brand_id
                ad_dict['description'] = description
                ad_dict['start_time'] = start_date
                ad_dict['ad_type'] = ad_type
                if languages:
                    ad_dict['languages'] = languages

                if end_date:
                    ad_dict['end_time'] = datetime.strptime(end_date, "%m/%d/%Y %I:%M %p")
                else:
                    ad_dict['end_time'] = None
                if toggler=='link' and ad_video_file_link:
                    ad_dict['video_file_url'] = ad_video_file_link
                ad_dict['frequency_type'] = toggler_frequency
                ad_dict['created_by_id'] = request.user.id
                if ad_type=="shop_now" and product_id!='-1':
                    discount_price = float(mrp) - float(discount)
                    Product.objects.filter(id=product_id).update(is_discounted=True, discounted_price=discount_price)
                    ad_dict['product_id'] = product_id
                else:
                    ad_dict['product_id'] = None
                if ad_video_file:
                    ad_folder_key_url = upload_media(s3_client, ad_video_file, ad_folder_key)
                    if not ad_folder_key_url:
                        return HttpResponse(json.dumps({'message':'fail','reason':'Failed to upload video file'}),content_type="application/json")
                    else:
                        ad_dict['video_file_url'] = ad_folder_key_url
                if not ad_id:
                    if not state:
                        state = "active"
                    ad_dict['state'] = state
                    ad_obj = Ad.objects.create(**ad_dict)
                    ad_id = ad_obj.id
                else:
                    if state:
                        ad_dict['state'] = state
                    ad_obj = Ad.objects.filter(id=ad_id)
                    ad_obj.update(**ad_dict)
                    ad_obj[0].cta.all().delete()
                    ad_obj[0].frequency.all().delete()

                scrolls = list(filter(bool,scrolls))
                #create frequency objects
                for index,value in enumerate(scrolls):
                    if value:
                        Frequency(ad_id=ad_id,sequence=index+1,scroll=value).save()
                #add cta
                cta_list = []
                if cta_type_1:
                    cta_list.append(cta_type_1)
                if cta_type_2:
                    cta_list.append(cta_type_2)
                for value in cta_list:
                    action = None
                    print(value)
                    title = CTA_OPTIONS[value]
                    if value.strip()!="skip":
                        # if cta_type_1_text:
                        #     title = cta_type_1_text
                        if value.strip()=="install_now":
                            action = playstore_link
                        elif value.strip()=="learn_more":
                            action = website_link
                    CTA(ad_id=ad_id, title=title, action=action, code=value).save()

                return HttpResponse(json.dumps({'message':'success', 'ad_id':ad_id}),content_type="application/json")
            except Exception as e:
                print(e)
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

def upload_media(client, media_file, key="media/"):
    try:
        from drf_spirit.views import remove_extra_char
        from jarvis.views import urlify
        # client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
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
            data = list(Product.objects.filter(name__istartswith=query).values('id','name','mrp','description'))
            return JsonResponse({'data': data}, status=status.HTTP_200_OK )
    except Exception as e:
        print(e)
        return JsonResponse({'data': [], 'error': str(e)}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        state = {}

        for row in query_fetch_data("""
                        select state.id as state_id, state.name as state, city.id as city_id, city.name as city
                        from advertisement_city city
                        inner join advertisement_state state on state.id = city.state_id
                    """):
            state_id = row.get('state_id')
            if not state.get(state_id):
                state[state_id] = {
                    'state_id': state_id,
                    'state': row.get('state'),
                    'cities': [{
                        'city': row.get('city'),
                        'city_id': row.get('city_id')
                    }]
                }
            else:
                state[state_id]['cities'].append({
                    'city': row.get('city'),
                    'city_id': row.get('city_id')
                })

        return Response({'results': state.values()}, status=200)

class OrderPaymentRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kawrgs):
        print "request data", self.request.resolver_match.kwargs
        order_id = self.request.resolver_match.kwargs.get('order_id')
        order = Order.objects.get(id=order_id)

        order.payment_status = 'initiated'

        # webengage_event.delay({
        #     "userId": booking.user_id,
        #     "eventName": "Booking Payment Initiated",
        #     "eventData": {
        #         "event_booking_id": booking.id,
        #         "event_id": booking.event.id,
        #         "event_slot_id": booking.event_slot_id,
        #         "slot_status": booking.event_slot.state,
        #         "booking_status": booking.state,
        #         "payment_status": booking.payment_status,
        #         "creator_id": booking.user_id,
        #         "booker_id": booking.event.creator_id,
        #         "slot_start_time": booking.event_slot.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        #         "slot_end_time": booking.event_slot.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        #     }

        # })

        if not order.payment_gateway_order_id:
            razorpay_order = create_order(order.amount_including_tax, "INR", receipt=order.order_number, notes={})
            order.payment_gateway_order_id = razorpay_order.get('id')
            order.paid_amount = order.amount_including_tax

        order.save()
        return '/payment/razorpay/%s/pay?type=order&order_id=%s'%(order.payment_gateway_order_id, order.id)

@login_required
def brand_management(request):
    return render(request,'advertisement/brand/brand_onboard_form_admin.html',{})

@login_required
def product_management(request):
    return render(request,'advertisement/product/product_onboard_form_admin.html',{})

@login_required
def particular_ad(request, ad_id=None):
    if request.user.is_superuser or 'moderator' in list(request.user.groups.all().values_list('name',flat=True)) or request.user.is_staff:
        ad_type_options_values = []
        cta_options_values = []
        for value1, value2 in CTA_OPTIONS.items():
            if value1!='skip':
                cta_options_values.append({'id':value1, 'value':value2})
        for value1, value2 in ad_type_options:
            ad_type_options_values.append({'id':value1, 'value':value2})
        ad = Ad.objects.get(pk=ad_id)
        product_desc = ""
        if ad.product:
            product_desc = ad.product.description.replace("\r"," ").replace("\n"," ")
        lang_options = []
        ad_languages = ad.languages
        for id_,value in language_options:
            data = {'id':id_, 'value':value,'select': False}
            if id_ in ad_languages:
                data['select'] = True
            lang_options.append(data)
        return render(request,'advertisement/ad/particular_ad.html', {'ad': ad, 'ad_type_options':ad_type_options_values,'cta_options': cta_options_values,'desc': product_desc, 'lang_options':lang_options})
    else:
        return JsonResponse({'error':'User Not Authorised','message':'fail' }, status=status.HTTP_200_OK)

class AdEventCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        data.update({
            'user_id': request.user.id,
            'created_at': datetime.now()
        })
        dynamodb_create(AdEvent, data)

        if data.get('event') in ('skip',):
            redis_key = 'ad:user:%s:skip'%request.user.id
            redis_cli.rpush(redis_key, data.get('ad_id'))
            
            if redis_cli_read_only.ttl(redis_key) in (-1, -2):
                now = datetime.now()
                print 'seconds', (datetime.strptime('%s-%s-%s 23:59:59'%(now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S') - now).seconds
                redis_cli.expire(redis_key, (datetime.strptime('%s-%s-%s 23:59:59'%(now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S') - now).seconds )

        return Response({'message': 'SUCCESS'}, status=201)


class GetAdForUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        params = request.query_params
        user_ad = {}
        ad_pool = get_redis('ad:pool')
        skipped_ad_list = redis_cli_read_only.lrange('ad:user:%s:skip'%params.get('user_id'), 0, -1)

        if not ad_pool:
            return Response({'results': {}})

        for key, items in ad_pool.iteritems():
            new_ad_list = []

            for ad in items:
                if str(ad.get('id'))  not in skipped_ad_list:
                    new_ad_list.append(ad)

            ad_pool[key] = new_ad_list

        next_position = 0
        ad_selection_history = {}

        ad_sequence = []
        for key, items in ad_pool.iteritems():
            ad_sequence += [key]*len(items)

        for scroll in sorted(map(int, ad_sequence )):
            next_position += scroll

            ad_list = ad_pool.get(str(scroll))
            min_value = ad_selection_history.get(ad_list[0].get('id'), 0)
            min_value_index = 0

            for i, ad in enumerate(ad_list):
                ad_min_value = ad_selection_history.get(ad.get('id'), 0)
                if ad_min_value < min_value: 
                    min_value = ad_min_value
                    min_value_index = i
                
            ad = ad_list.pop(min_value_index)
            ad_selection_history[ad.get('id')] = next_position

            user_ad[str(next_position)] = get_redis('ad:%s'%ad.get('id'))  # Todo: Need to imporve it

        return Response({
            'results': user_ad
        })

from multiprocessing.sharedctypes import Value

class DashBoardCountAPIView(APIView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request, *args, **kwargs):
        lock = Lock()
        today = datetime.now()

        query_list = (
            ('ongoing_ad', Ad.objects.filter(state='ongoing'), Value('i', 0, lock=lock)),
            ('upcoming_ad', Ad.objects.filter(start_time__gte=today), Value('i', 0, lock=lock)),
            ('added_to_draft', Ad.objects.filter(state='draft'), Value('i', 0, lock=lock)),
            ('onboarded_products', Product.objects.filter(is_active=True), Value('i', 0, lock=lock)),
            ('impressions', Seen.objects.all(), Value('i', 0, lock=lock)),
            ('skips', Skipped.objects.all(), Value('i', 0, lock=lock)),
            ('install_click', Clicked.objects.filter(cta='install'), Value('i', 0, lock=lock)),
            ('shop_now_click', Clicked.objects.filter(cta='shop_now'), Value('i', 0, lock=lock)),
            ('brand_onboarded', Brand.objects.filter(is_active=True), Value('i', 0, lock=lock)),
            ('learn_more_click', Clicked.objects.filter(cta='learn_more'), Value('i', 0, lock=lock)),
            ('lifetime_order', Order.objects.exclude(state='draft'), Value('i', 0, lock=lock)),
            ('unique_order', Order.objects.exclude(state='draft').distinct('user_id'), Value('i', 0, lock=lock)),
            ('month_order', Order.objects.filter(date__gte='%s-%s-01'%(today.year, today.month)).exclude(state='draft'), Value('i', 0, lock=lock)),
            ('onboarded_brands', Brand.objects.all(), Value('i', 0, lock=lock)),
            ('unique_products', Product.objects.all(), Value('i', 0, lock=lock)),
        )

        processes = []

        for args in query_list:
            self.get_count(*args)
            # processes.append(Process(target=self.get_count, args=args))

        # for p in processes:
        #     p.start()

        # print "processed started"
        # for p in processes:
        #     p.join()

        # print "prcessed joinede"
        return Response({args[0]: args[2].value  for args in query_list})

    def get_count(self, key, query, val_container):
        val_container.value = query.count()

class AdTemplateView(TemplateView):
    template_name = 'advertisement/ad/index.html'


class OrderTemplateView(TemplateView):
    template_name = 'advertisement/order/dashboard.html'

class ProductTemplateView(TemplateView):
    template_name = 'advertisement/product/index.html'

class OrderDashboardLogin(LoginView):
    template_name = 'advertisement/order/login.html'
    success_url = '/ad/order/'

    def get_success_url(self):
        return self.success_url

    # def post(self, request, *args, **kwargs):
    #     print 'request posrt data', request.POST
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     user = authenticate(request, username=username, password=password)
    #     if user is not None:
    #         login(request, user)
    #     else:

class OrderDashboardLogout(LogoutView):
    # template_name = 'advertisement/order/login.html'
    next_page = '/ad/login/'

class OrderPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'advertisement/order/reset_password.html'
    success_url = '/ad/login/?password_changed=success'


class OrderPasswordResetMailView(PasswordResetView):
    template_name = 'advertisement/order/login.html'
    success_url = '/ad/login/?reset_password=success'
    html_email_template_name = 'advertisement/order/password_reset_email.html'
    email_template_name = 'advertisement/order/password_reset_email.html'


class FilterDataAPIView(APIView):
    def get(self, request, *args, **kwargs):
        print "request.query_params", request.query_params
        filter_type = request.query_params.get('type')

        if filter_type == 'amount':
            return Response({
                'min': DatabaseRecordCount.get_value('ad_order_amount_min'),
                'max': DatabaseRecordCount.get_value('ad_order_amount_max')
            })
        elif filter_type == 'product':
            name = request.query_params.get('name')
            brand_id = request.query_params.get('brand_id')
            sort = request.query_params.get('sort')

            queryset = Product.objects.all()

            if name:
                queryset = Product.objects.filter(name__icontains=name)

            if brand_id:
                queryset = queryset.filter(brand_id=brand_id)

            if sort and sort == 'desc':
                queryset = queryset.order_by('-name')
            else:
                queryset = queryset.order_by('name')

            return Response({
                'results': queryset.values('id', 'name')
            })

class ChartDataAPIView(APIView):
    WEEK_ENUM = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    MONTH_ENUM = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    def get(self, request, *args, **kwargs):
        chart_type = request.query_params.get('chart_type')
        data_type = request.query_params.get('data_type')
        cursor = connections['read'].cursor()

        result = [[], []]

        if chart_type == 'order':
            if data_type == 'weekly':
                cursor.execute("""
                    select extract(isodow from date)::integer - 1 as weekday, count
                    from (
                        select date::date, count(1)
                        from advertisement_order
                        where date >= now() - interval '7 days' and state != 'draft'
                        group by date::date
                    ) A
                """)
                result = self.get_weekly_data(self.dictfetchall(cursor))
                
            elif data_type == 'monthly':
                today = datetime.now()
                cursor.execute("""
                    select extract(day from date)::integer, count
                    from (
                        select date::date, count(1)
                        from advertisement_order
                        where date >= %s and state != 'draft'
                        group by date::date
                    ) A
                """, ['%s-%s-01'%(today.year, today.month)])
                result = self.get_monthly_data(self.dictfetchall(cursor))

            elif data_type == 'yearly':
                today = datetime.now()
                cursor.execute("""
                    select extract(month from date)::integer, count
                    from (
                        select DATE_TRUNC('month', date) as date, count(1)
                        from advertisement_order
                        where date >= %s and state != 'draft'
                        group by DATE_TRUNC('month', date)
                    ) A
                """, ['%s-01-01'%(today.year)])
                result = self.get_yearly_data(self.dictfetchall(cursor))

            elif data_type == 'lifetime':
                today = datetime.now()
                cursor.execute("""
                    select extract(month from date)::integer, count
                    from (
                        select DATE_TRUNC('month', date) as date, count(1)
                        from advertisement_order
                        where date >= %s and state != 'draft'
                        group by DATE_TRUNC('month', date)
                    ) A
                """, ['%s-01-01'%(today.year)])
                result = self.get_yearly_data(self.dictfetchall(cursor))

        elif chart_type == 'revenue':
            if data_type == 'weekly':
                cursor.execute("""
                    select extract(isodow from date)::integer - 1 as weekday, amount
                    from (
                        select date::date, sum(amount) as amount
                        from advertisement_order
                        where date >= now() - interval '7 days' and state != 'draft'
                        group by date::date
                    ) A
                """)
                result = self.get_weekly_data(self.dictfetchall(cursor))
                
            elif data_type == 'monthly':
                today = datetime.now()
                cursor.execute("""
                    select extract(day from date)::integer, amount
                    from (
                        select date::date, sum(amount) as amount
                        from advertisement_order
                        where date >= %s and state != 'draft'
                        group by date::date
                    ) A
                """, ['%s-%s-01'%(today.year, today.month)])
                result = self.get_monthly_data(self.dictfetchall(cursor))

            elif data_type == 'yearly':
                today = datetime.now()
                cursor.execute("""
                    select extract(month from date)::integer, amount
                    from (
                        select DATE_TRUNC('month', date) as date, sum(amount) as amount
                        from advertisement_order
                        where date >= %s and state != 'draft'
                        group by DATE_TRUNC('month', date)
                    ) A
                """, ['%s-01-01'%(today.year)])
                result = self.get_yearly_data(self.dictfetchall(cursor))

            elif data_type == 'lifetime':
                today = datetime.now()
                cursor.execute("""
                    select extract(month from date)::integer, amount
                    from (
                        select DATE_TRUNC('month', date) as date, sum(amount) as amount
                        from advertisement_order
                        where date >= %s and state != 'draft'
                        group by DATE_TRUNC('month', date)
                    ) A
                """, ['%s-01-01'%(today.year)])
                result = self.get_yearly_data(self.dictfetchall(cursor))

        return Response({
            'labels': result[0],
            'dataset': result[1],
        })

    def dictfetchall(self, cursor):
        return {
            row[0]: row[1] for row in cursor.fetchall()
        }

    def get_weekly_data(self, query_data):
        print "query data", query_data
        start_date = datetime.now() - timedelta(days=7)
        labels = []
        dataset = []

        for i in range(7):
            weekday = (start_date + timedelta(days=i+1)).weekday()
            print "weekday", weekday
            labels.append(self.WEEK_ENUM[weekday])
            dataset.append(query_data.get(weekday, 0))
        
        return labels, dataset

    def get_monthly_data(self, query_data):
        print "query data", query_data
        today = datetime.now()
        start_date = datetime.strptime('01-%s-%s'%(today.month, today.year), '%d-%m-%Y')
        day_diff = (today - start_date).days + 1
        print "day_diff", day_diff
        labels = []
        dataset = []

        for day in range(1, day_diff+1):
            labels.append(day)
            dataset.append(query_data.get(day, 0))
        
        return labels, dataset

    def get_yearly_data(self, query_data):
        print "query data", query_data
        today = datetime.now() 
        labels = []
        dataset = []

        for month in range(today.month):
            print "month", month
            labels.append(self.MONTH_ENUM[month])
            dataset.append(query_data.get(month+1, 0))
        
        return labels, dataset


class ChangePasswordAPIView(UpdateAPIView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user
