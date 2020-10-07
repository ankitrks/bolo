from datetime import datetime
from copy import deepcopy

from django.views.generic import TemplateView, DetailView
from django.db import connections
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from payment.utils import PageNumberPaginationRemastered
from payment.permission import UserPaymentPermissionView
from payment.partner.models import Beneficiary, TopUser
from payment.partner.serializers import BeneficiarySerializer, TopUserSerializer


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



def month_year_iter(start_month, start_year, end_month, end_year):
    yield "%s-%s-01"%(start_year, str(start_month).zfill(2))

    while start_month < end_month or start_year < end_year:
        start_month += 1

        if start_month > 12:
            start_year += 1
            start_month = 1

        yield "%s-%s-01"%(start_year, str(start_month).zfill(2))



class TopUserTemplateView(UserPaymentPermissionView, TemplateView):
    template_name = "payment/partner/top_users/index.html"


    def get_context_data(self, **kwargs):
        print("request", self.request.__dict__)
        context = super(TopUserTemplateView, self).get_context_data(**kwargs)
        today = datetime.now().date()

        context['all_month'] = sorted([{
            'name': datetime.strptime(month, '%Y-%m-%d').strftime('%B %Y'),
            'value': month
        } for month in month_year_iter(1, 2020, today.month, today.year)], key=lambda x: x.get('value'), reverse=True)

        print("All months", context['all_month'])
        return context





class TopUserListView(UserPaymentPermissionView, ListAPIView):
    queryset = TopUser.objects.all()
    serializer_class = TopUserSerializer
    pagination_class = PageNumberPaginationRemastered

    def get_queryset(self):
        print("request", self.request.query_params)
        query_params = self.request.query_params
        queryset = self.queryset

        sort_field = '-video_count'
        
        if query_params.get('sortField'):
            sort_field = query_params.get('sortField')

        if query_params.get('sortOrder') == 'desc':
            sort_field = '-' + sort_field

        if query_params.get('selectedMonth'):
            print("selectedMonth", query_params.get('selectedMonth'))
            date = datetime.strptime(query_params.get('selectedMonth'), '%Y-%m-%d')
            self.queryset = self.queryset.filter(agg_month=query_params.get('selectedMonth'))

        if query_params.get('q'):
            q = query_params.get('q')
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    SELECT user_id
                    FROM forum_user_userprofile
                    WHERE name ilike %s or slug = %s
                """, ['%' + q +'%', q])
                ids = [row[0] for row in cursor.fetchall()]

            self.queryset = self.queryset.filter(boloindya_id__in=ids)


        query = self.queryset.query.sql_with_params()
        print(query[0]%query[1])

        return self.queryset.order_by(sort_field)
