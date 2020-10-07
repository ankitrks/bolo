from copy import deepcopy

from django.shortcuts import render
from django.views.generic import TemplateView
from django.db import connections
from django.http import JsonResponse

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from payment.permission import UserPaymentPermissionView, PaymentPermission
from payment.utils import PageNumberPaginationRemastered
from payment.partner.models import Beneficiary
from payment.payout.models import ScheduledPayment, Transaction
from payment.payout.serializers import ScheduledPaymentSerializer, TransactionSerializer, PaySerializer


class PaymentStatusView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/payout/payment/index.html"



class ScheduledPaymentView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/payout/scheduled_payment/index.html"


class ScheduledPaymentModelViewSet(ModelViewSet):
    queryset = ScheduledPayment.objects.all()
    serializer_class = ScheduledPaymentSerializer
    pagination_class = PageNumberPaginationRemastered
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def create(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        print "request.user", request.user
        data.update({
            'created_by': request.user.id,
        })
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def get_queryset(self):
        print(" queryset request", self.request.parser_context.get('kwargs', {}).get('beneficiary'))
        if self.request.parser_context.get('kwargs', {}).get('beneficiary'):
            return self.queryset.filter(beneficiary_id=self.request.parser_context.get('kwargs', {}).get('beneficiary'))

        return self.queryset



class TransactionView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/payout/transaction/index.html"


class TransactionListAPIView(ListAPIView):
    queryset = Transaction.objects.all().order_by('-transaction_date')
    serializer_class = TransactionSerializer
    pagination_class = PageNumberPaginationRemastered
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)


class PayAPIView(APIView):
    serializer_class = PaySerializer
    permission_classes = (IsAuthenticated, PaymentPermission)
    authentication_classes = (SessionAuthentication,)

    def post(self, request, *args, **kwargs):
        print("request data", request.data)
        user_id = request.data.get('user_id')
        beneficiary_id = self.request.parser_context.get('kwargs', {}).get('beneficiary')

        beneficiary = Beneficiary.objects.filter(id=beneficiary_id)
        if beneficiary:
            beneficiary = beneficiary[0]

        beneficiary.transfer(request.data.get('amount'))

        return JsonResponse({
                'status': 'success'
            }, status=200, content_type='application/json')



