# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from copy import deepcopy
from datetime import datetime
from multiprocessing import Process, Pool, Manager, Lock

from django.shortcuts import render
from django.db.models import Sum, Q
from django.test import Client
from django.views.generic import RedirectView, TemplateView, DetailView

from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIClient

from dynamodb_api import create as dynamodb_create
from redis_utils import get_redis
from payment.razorpay import create_order

from advertisement.utils import query_fetch_data, convert_to_dict_format, filter_data_from_dict, PageNumberPaginationRemastered
from advertisement.models import (Ad, ProductReview, Order, Product, Address, OrderLine, AdEvent,
                                    Seen, Skipped, Clicked, Brand)
from advertisement.serializers import (AdSerializer, ReviewSerializer, OrderSerializer, ProductSerializer, AddressSerializer, 
                                        OrderCreateSerializer, OrderLineSerializer)



class AdDetailAPIView(RetrieveAPIView):
    queryset = Ad.objects.filter(state='active')
    serializer_class = AdSerializer


class ProductDetailAPIView(RetrieveAPIView):
    queryset = Ad.objects.filter(state='active')
    serializer_class = ProductSerializer    

    def get_object(self):
        obj = super(ProductDetailAPIView, self).get_object()
        return obj.product


class AdViewset(ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    pagination_class = deepcopy(PageNumberPaginationRemastered)

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        page_size = self.request.query_params.get('page_size')
        brand_name = self.request.query_params.get('brand_name')
        product_name = self.request.query_params.get('product_name')

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

        if page_size:
            self.pagination_class.page_size = int(page_size)

        return queryset.order_by('id')



class ReviewListAPIView(ListAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.request.parser_context.get('kwargs', {}).get('product_id')
        return self.queryset.filter(product_id=product_id)


class AddressViewset(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderViewset(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        client = APIClient()
        request_data = deepcopy(request.data)
        request_meta = request.META

        """ Saving Address """
        address_data = filter_data_from_dict(['name', 'mobile', 'address1', 'address2', 'address3', 'city_id', 'state_id', 'pincode'], request.data)
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
            order = client.patch('/api/v1/ad/order/%s/'%request_data.pop('order_id'), order_data, HTTP_AUTHORIZATION=request_meta.get('HTTP_AUTHORIZATION'), format='json').json()
        else:
            order = client.post('/api/v1/ad/order/', order_data, HTTP_AUTHORIZATION=request_meta.get('HTTP_AUTHORIZATION'), format='json').json()
        return Response(order, status=status.HTTP_201_CREATED)



class CityListAPIView(APIView):
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
            razorpay_order = create_order(order.amount, "INR", receipt=order.order_number, notes={})
            order.payment_gateway_order_id = razorpay_order.get('id')

        order.save()
        return '/payment/razorpay/%s/pay?type=order&order_id=%s'%(order.payment_gateway_order_id, order.id)


class AdEventCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        data.update({
            'user_id': request.user.id,
            'created_at': datetime.now()
        })
        dynamodb_create(AdEvent, data)
        return Response({'message': 'SUCCESS'}, status=201)


class GetAdForUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        params = request.query_params
        user_ad = {}
        ad_pool = get_redis('ad:pool')
        next_position = 0

        for scroll in sorted(map(int, ad_pool.keys())):
            next_position += scroll
            user_ad[str(next_position)] = get_redis('ad:%s'%ad_pool.get(str(scroll))[0].get('id'))  # Todo: Need to imporve it

        return Response({
            'results': user_ad
        })

from multiprocessing.sharedctypes import Value

class DashBoardCountAPIView(APIView):
    def get(self, request, *args, **kwargs):
        lock = Lock()

        query_list = (
            ('ongoing_ad', Ad.objects.filter(state='active', start_time__lte=datetime.now(), end_time__gte=datetime.now()), Value('i', 0, lock=lock)),
            ('upcoming_ad', Ad.objects.filter(start_time__gte=datetime.now()), Value('i', 0, lock=lock)),
            ('added_to_draft', Ad.objects.filter(state='draft'), Value('i', 0, lock=lock)),
            ('onboarded_products', Product.objects.filter(is_active=True), Value('i', 0, lock=lock)),
            ('impressions', Seen.objects.all(), Value('i', 0, lock=lock)),
            ('skips', Skipped.objects.all(), Value('i', 0, lock=lock)),
            ('install_click', Clicked.objects.filter(cta='install'), Value('i', 0, lock=lock)),
            ('shop_now_click', Clicked.objects.filter(cta='shop_now'), Value('i', 0, lock=lock)),
            ('brand_onboarded', Brand.objects.filter(is_active=True), Value('i', 0, lock=lock)),
            ('learn_more_click', Clicked.objects.filter(cta='learn_more'), Value('i', 0, lock=lock))
        )

        processes = []

        for args in query_list:
            print "creating process"
            self.get_count(*args)
            # processes.append(Process(target=self.get_count, args=args))

        print "processes", processes
        # for p in processes:
        #     p.start()

        # print "processed started"
        # for p in processes:
        #     p.join()

        # print "prcessed joinede"
        print "returnong response"
        return Response({args[0]: args[2].value  for args in query_list})

    def get_count(self, key, query, val_container):
        print "getting count "
        val_container.value = query.count()
        print "writing done"

class AdTemplateView(TemplateView):
    template_name = 'advertisement/ad/index.html'


class OrderTemplateView(TemplateView):
    template_name = 'advertisement/order/index.html'


