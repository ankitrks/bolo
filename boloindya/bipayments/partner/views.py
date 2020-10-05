from datetime import datetime

from django.views.generic import TemplateView, DetailView

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from bipayments.utils import PageNumberPaginationRemastered
from bipayments.partner.models import Beneficiary, TopUser
from bipayments.partner.serializers import BeneficiarySerializer, TopUserSerializer



class BeneficiaryTemplateView(TemplateView):
    template_name = "partner/beneficiary/index.html"


class BeneficiaryViewSet(ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer

    def create(self, request, *args, **kwargs):
        print("request data create BeneficiaryViewSet", request.data)
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        print("request data partial_update BeneficiaryViewSet", request.data)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class BeneficiaryDetailTemplateView(DetailView):
    template_name = "partner/beneficiary/beneficiary_details.html" 
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



class TopUserTemplateView(TemplateView):
    template_name = "partner/top_users/index.html"



    def get_context_data(self, **kwargs):
        context = super(TopUserTemplateView, self).get_context_data(**kwargs)
        today = datetime.now().date()

        context['all_month'] = sorted([{
            'name': datetime.strptime(month, '%Y-%m-%d').strftime('%B %Y'),
            'value': month
        } for month in month_year_iter(1, 2020, today.month, today.year)], key=lambda x: x.get('value'), reverse=True)

        print("All months", context['all_month'])
        return context





class TopUserListView(ListAPIView):
    queryset = TopUser.objects.all()
    serializer_class = TopUserSerializer
    pagination_class = PageNumberPaginationRemastered

    def get_queryset(self):
        print("request", self.request.query_params)
        queryset = self.queryset

        sort_field = '-video_count'
        
        if self.request.query_params.get('sortField'):
            sort_field = self.request.query_params.get('sortField')

        if self.request.query_params.get('sortOrder') == 'desc':
            sort_field = '-' + sort_field

        if self.request.query_params.get('selectedMonth'):
            print("selectedMonth", self.request.query_params.get('selectedMonth'))
            date = datetime.strptime(self.request.query_params.get('selectedMonth'), '%Y-%m-%d')
            self.queryset = self.queryset.filter(agg_month=self.request.query_params.get('selectedMonth'))


        query = self.queryset.query.sql_with_params()
        print(query[0]%query[1])

        return self.queryset.order_by(sort_field)
