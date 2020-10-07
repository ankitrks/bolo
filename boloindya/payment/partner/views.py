from datetime import datetime
from copy import deepcopy
import csv
import io

from django.views.generic import TemplateView, DetailView
from django.db import connections
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from payment.utils import PageNumberPaginationRemastered
from payment.permission import UserPaymentPermissionView
from payment.partner.models import Beneficiary, TopUser
from payment.partner.serializers import BeneficiarySerializer


class BeneficiaryTemplateView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/partner/beneficiary/index.html"


class BeneficiaryViewSet(UserPaymentPermissionView, ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    pagination_class = PageNumberPaginationRemastered
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def create(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        print "request.user", request.user
        data.update({
            'created_by': request.user.id,
            'modified_by': request.user.id
        })
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = deepcopy(request.data)
        data['modified_by'] = request.user.id
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        q = self.request.query_params.get('q')
        if q:
            self.queryset = self.queryset.filter(Q(name__icontains=q) | Q(paytm_number=q) | Q(upi=q) | Q(account_number=q))

        return self.queryset

class BeneficiaryDetailTemplateView(UserPaymentPermissionView, DetailView):
    template_name = "payment/partner/beneficiary/beneficiary_details.html" 
    queryset = Beneficiary.objects.all()


    def get_context_data(self, **kwargs):
        context = super(BeneficiaryDetailTemplateView, self).get_context_data(**kwargs)
        top_user = TopUser.objects.filter(boloindya_id=context.get('object').boloindya_id)

        if top_user:
            context['detail'] = top_user[0]
            
        return context

class BeneficiaryBulkCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)


    def post(self, request, *args, **kwargs):
        csvfile = csv.DictReader(io.StringIO(request.data.get('beneficiary_file').read().decode('utf-8')))
        user_ids = [row.get('user_id') for row in csvfile]

        print 'user_ids', user_ids
        if not user_ids:
            return Response({})


        cursor = connections['default'].cursor()
        cursor.execute("""
            SELECT user_id as boloindya_id, COALESCE(name, slug, '') as name, paytm_number  
            FROM forum_user_userprofile 
            WHERE user_id in %s
        """, [tuple(user_ids)])

        columns = [col[0] for col in cursor.description]
        user_data_list = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        print "user_data_list", user_data_list
        beneficiary_list = []
        
        for user_data in user_data_list:
            user_data.update({
                'payment_method': 'paytm_wallet',
                'verification_status': 'pending',
                'created_by_id': request.user.id,
                'modified_by_id':request.user.id
            })
            beneficiary_list.append(Beneficiary(**user_data))

        print "beneficiary_list", beneficiary_list

        Beneficiary.objects.bulk_create(beneficiary_list)

        return Response({})
