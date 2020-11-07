# -*- coding: utf-8 -*-
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
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.request.parser_context.get('kwargs', {}).get('product_id')
        return self.queryset.filter(product_id=product_id)


class OrderListCreateAPIView(ListCreateAPIView):
    queryset = Order.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class CityListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return {}