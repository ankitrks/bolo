from django.shortcuts import render
from django.views.generic import TemplateView
from django.db import connections
from django.http import JsonResponse

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from payment.permission import UserPaymentPermissionView
from payment.utils import PageNumberPaginationRemastered
from payment.partner.models import Beneficiary
from payment.payout.models import ScheduledPayment, Transaction
from payment.payout.serializers import ScheduledPaymentSerializer, TransactionSerializer, PaySerializer


class PaymentStatusView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/payout/payment/index.html"



class ScheduledPaymentView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/payout/scheduled_payment/index.html"


class ScheduledPaymentModelViewSet(UserPaymentPermissionView, ModelViewSet):
    queryset = ScheduledPayment.objects.all()
    serializer_class = ScheduledPaymentSerializer
    pagination_class = PageNumberPaginationRemastered

    def create(self, request, *args, **kwargs):
        print("request data ScheduledPaymentModelViewSet", request.data)
        return super(ScheduledPaymentModelViewSet, self).create(request, *args, **kwargs)

    def get_queryset(self):
        print(" queryset request", self.request.parser_context.get('kwargs', {}).get('beneficiary'))
        if self.request.parser_context.get('kwargs', {}).get('beneficiary'):
            return self.queryset.filter(beneficiary_id=self.request.parser_context.get('kwargs', {}).get('beneficiary'))

        return self.queryset



class TransactionView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/payout/transaction/index.html"


class TransactionListAPIView(UserPaymentPermissionView, ListAPIView):
    queryset = Transaction.objects.all().order_by('-transaction_date')
    serializer_class = TransactionSerializer
    pagination_class = PageNumberPaginationRemastered


class PayAPIView(UserPaymentPermissionView, APIView):
    serializer_class = PaySerializer

    def post(self, request, *args, **kwargs):
        print("request data", request.data)
        user_id = request.data.get('user_id')

        beneficiary = Beneficiary.objects.filter(boloindya_id=user_id)
        if beneficiary:
            beneficiary = beneficiary[0]
        else:
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    SELECT user_id as boloindya_id, COALESCE(name, slug, '') as name, paytm_number  
                    FROM forum_user_userprofile 
                    WHERE user_id = %s
                """, [user_id])

                columns = [col[0] for col in cursor.description]
                user_data = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            if user_data:
                user_data = user_data[0]

            print("user data", user_data)

            user_data.update({
                'payment_method': 'paytm_wallet',
                'verification_status': 'verified',
                'paytm_number': request.data.get('paytm_number') or user_data.get('paytm_number')
            })

            beneficiary = Beneficiary.objects.create(**user_data)

        beneficiary.transfer(request.data.get('amount'))

        return JsonResponse({
                'status': 'success'
            }, status=200, content_type='application/json')



