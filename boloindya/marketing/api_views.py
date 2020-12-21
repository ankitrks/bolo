import pandas as pd
import json
from copy import deepcopy
from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import intword
from django.contrib.auth.models import User
from django.db import connections

from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from drf_spirit.models import DatabaseRecordCount

from advertisement.utils import PageNumberPaginationRemastered
from advertisement.models import Brand

from marketing.models import AdStats
from marketing.serializers import AdStatsSerializer, AdCreatorSerializer, AdBrandSerializer


class BaseMarketingAPIView:
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)


class AdStatsListAPIView(ListAPIView):
    serializer_class = AdStatsSerializer
    queryset = AdStats.objects.all()
    pagination_class = deepcopy(PageNumberPaginationRemastered)
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        print 'queryset', queryset
        # print pd.DataFrame(queryset.values('ad_id', 'full_watched', 'install_count', 'skip_playtime', 'install_playtime', 'skip_count', 
        #                 'view_count', 'ad__title', 'ad__created_by__username' ))
        dataframe = pd.DataFrame(queryset.values('ad_id', 'full_watched', 'install_count', 'skip_playtime', 'install_playtime', 'skip_count', 
                        'view_count', 'ad__product__name', 'ad__created_by__username' ))
        
        if dataframe.empty:
            return Response({
                'data': [],
                'itemsCount': 0
        })
        print "datafram", json.loads(dataframe.to_json(orient="table")).get('data')
        dataframe = dataframe.groupby(['ad_id', 'ad__created_by__username']).sum()

        dataframe['average_install_time'] = dataframe['install_playtime'] / dataframe['install_count']
        dataframe['average_skip_time'] = dataframe['skip_playtime'] / dataframe['skip_count']
        dataframe['ctr'] = dataframe['install_count'] / dataframe['view_count']

        if request.query_params.get('sortField'):
            dataframe = dataframe.sort_values(by=request.query_params.get('sortField'), 
                                                ascending=True if request.query_params.get('sortOrder') == 'asc' else False)


        page = int(request.query_params.get('page', '1'))
        page_size = int(request.query_params.get('page_size', '10'))

        #print "page", page, "page_size", page_size
        #print "datafram", json.loads(dataframe.to_json(orient="table")).get('data')
        #print "data", json.loads(dataframe[(page - 1) * page_size:(page) * page_size].round(2).to_json(orient="table")).get('data')

        return Response({
            'data': json.loads(dataframe[(page - 1) * page_size:(page) * page_size].round(2).to_json(orient="table")).get('data'),
            'itemsCount': len(dataframe)
        })

    def get_queryset(self):
        queryset = self.queryset
        creators = self.request.query_params.get('creators')
        brand = self.request.query_params.get('brand')
        date_range = self.request.query_params.get('date_range')

        if creators:
            queryset = queryset.filter(ad__created_by__in=creators.split(','))

        if brand:
            queryset = queryset.filter(ad__brand_id=brand)

        if date_range:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            print "start date", start_date, "end date", end_date
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date, ad__created_at__gte=start_date, ad__created_at__lte=end_date)

        return queryset


class AdCreatorAPIView(ListAPIView, BaseMarketingAPIView):
    serializer_class = AdCreatorSerializer
    queryset = User.objects.filter(is_staff=True)

    def get_queryset(self):
        q = self.request.query_params.get('q')

        if q:
            return self.queryset.filter(username__istartswith=q)

        return self.queryset


class AdBrandAPIView(ListAPIView, BaseMarketingAPIView):
    serializer_class = AdBrandSerializer
    queryset = Brand.objects.all()


class AdInstallChartDataAPIView(APIView):
    WEEK_ENUM = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    MONTH_ENUM = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    def get(self, request, *args, **kwargs):
        chart_type = request.query_params.get('chart_type')
        data_type = request.query_params.get('data_type')
        cursor = connections['read'].cursor()

        result = [[], []]

        if chart_type == 'views':
            if data_type == 'weekly':
                cursor.execute("""
                    select extract(isodow from date)::integer - 1 as weekday, count
                    from (
                        select date::date, sum(view_count) as count
                        from marketing_adstats
                        where date >= now() - interval '7 days'
                        group by date::date
                    ) A
                """)
                result = self.get_weekly_data(self.dictfetchall(cursor))
                
            elif data_type == 'monthly':
                today = datetime.now()
                cursor.execute("""
                    select extract(day from date)::integer, count
                    from (
                        select date::date, sum(view_count) as count
                        from marketing_adstats
                        where date >= %s
                        group by date::date
                    ) A
                """, ['%s-%s-01'%(today.year, today.month)])
                result = self.get_monthly_data(self.dictfetchall(cursor))

            elif data_type == 'yearly':
                today = datetime.now()
                cursor.execute("""
                    select extract(month from date)::integer, count
                    from (
                        select DATE_TRUNC('month', date) as date, sum(view_count) as count
                        from marketing_adstats
                        where date >= %s
                        group by DATE_TRUNC('month', date)
                    ) A
                """, ['%s-01-01'%(today.year)])
                result = self.get_yearly_data(self.dictfetchall(cursor))

        elif chart_type == 'installs':
            if data_type == 'weekly':
                cursor.execute("""
                    select extract(isodow from date)::integer - 1 as weekday, count
                    from (
                        select date::date, sum(install_count) as count
                        from marketing_adstats
                        where date >= now() - interval '7 days'
                        group by date::date
                    ) A
                """)
                result = self.get_weekly_data(self.dictfetchall(cursor))
                
            elif data_type == 'monthly':
                today = datetime.now()
                cursor.execute("""
                    select extract(day from date)::integer, count
                    from (
                        select date::date, sum(install_count) as count
                        from marketing_adstats
                        where date >= %s
                        group by date::date
                    ) A
                """, ['%s-%s-01'%(today.year, today.month)])
                result = self.get_monthly_data(self.dictfetchall(cursor))

            elif data_type == 'yearly':
                today = datetime.now()
                cursor.execute("""
                    select extract(month from date)::integer, count
                    from (
                        select DATE_TRUNC('month', date) as date, sum(install_count) as count
                        from marketing_adstats
                        where date >= %s
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
        # print "query data", query_data
        start_date = datetime.now() - timedelta(days=7)
        labels = []
        dataset = []

        for i in range(7):
            weekday = (start_date + timedelta(days=i+1)).weekday()
            # print "weekday", weekday
            labels.append(self.WEEK_ENUM[weekday])
            dataset.append(query_data.get(weekday, 0))
        
        return labels, dataset

    def get_monthly_data(self, query_data):
        # print "query data", query_data
        today = datetime.now()
        start_date = datetime.strptime('01-%s-%s'%(today.month, today.year), '%d-%m-%Y')
        day_diff = (today - start_date).days + 1
        # print "day_diff", day_diff
        labels = []
        dataset = []

        for day in range(1, day_diff+1):
            labels.append(day)
            dataset.append(query_data.get(day, 0))
        
        return labels, dataset

    def get_yearly_data(self, query_data):
        # print "query data", query_data
        today = datetime.now() 
        labels = []
        dataset = []

        for month in range(today.month):
            print "month", month
            labels.append(self.MONTH_ENUM[month])
            dataset.append(query_data.get(month+1, 0))
        
        return labels, dataset


class DashboadCountAPIView(APIView, BaseMarketingAPIView):
    def get(self, request, *args, **kwargs):
        counts = {}

        for item in request.query_params.get('queries').split(','):
            count = intword(DatabaseRecordCount.get_value(item))
            count_split = count.split(' ') if not type(count) == int else []

            if len(count_split) > 1:
                count = str(int(float(count_split[0]))) + ' ' + count_split[1].capitalize()[0]

            counts[item] = count

        return Response(counts)
