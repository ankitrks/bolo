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


class ReviewListAPIView(ListAPIView):
    queryset = ProductReview.objects.all()


class OrderListCreateAPIView(ListCreateAPIView):
    queryset = Order.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class CityListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return {}