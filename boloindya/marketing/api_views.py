import pandas as pd
import json
from copy import deepcopy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.humanize.templatetags.humanize import intword
from django.contrib.auth.models import User
from django.db import connections
from django.db.models import Sum, Min, Max, Q

from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from drf_spirit.models import DatabaseRecordCount

from forum.category.models import Category

from advertisement.utils import PageNumberPaginationRemastered
from advertisement.models import Brand, Ad

from booking.models import Event, EventBooking

from marketing.models import AdStats, EventStats
from marketing.serializers import (AdStatsSerializer, AdCreatorSerializer, AdBrandSerializer, EventBookingSerializer,
                                    CategorySerializer, EventStatsSerializer)


class BaseMarketingAPIView:
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)


class AdStatsListAPIView(ListAPIView):
    serializer_class = AdStatsSerializer
    queryset = AdStats.objects.filter(ad__ad_type='install_now')
    pagination_class = deepcopy(PageNumberPaginationRemastered)
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        print 'queryset', queryset
        # print pd.DataFrame(queryset.values('ad_id', 'full_watched', 'install_count', 'skip_playtime', 'install_playtime', 'skip_count', 
        #                 'view_count', 'ad__title', 'ad__created_by__username' ))
        dataframe = pd.DataFrame(queryset.values('ad_id', 'full_watched', 'install_count', 'skip_playtime', 'install_playtime', 'skip_count', 
                        'view_count' ))

        if dataframe.empty:
            return Response({
                'data': [],
                'itemsCount': 0
        })
        dataframe = dataframe.groupby(['ad_id']).sum()
        dataframe['average_install_time'] = dataframe['install_playtime'] / dataframe['install_count']
        dataframe['average_skip_time'] = dataframe['skip_playtime'] / dataframe['skip_count']
        dataframe['ctr'] = (dataframe['install_count'] / dataframe['view_count'])*100


        page = int(request.query_params.get('page', '1'))
        page_size = int(request.query_params.get('page_size', '10'))

        final_dataframe = dataframe.round(0)
        data = json.loads(dataframe.round(0).to_json(orient="table")).get('data')

        # print Ad.objects.filter(id__in=final_dataframe.axes[0]).values('id', 'brand__name', 'created_by__username')

        for ad in Ad.objects.filter(id__in=final_dataframe.axes[0]).values('id', 'brand__name', 'creator', 'state', 'start_time'):
            for item in data:
                if item.get('ad_id') == ad.get('id'):
                    item['ad__brand__name'] = ad.get('brand__name')
                    item['creator'] = ad.get('creator')
                    item['state'] = ad.get('state')
                    item['start_time'] = ad.get('start_time')

        if request.query_params.get('sortField'):
            sorted_data = sorted(data, key=lambda x: x.get(request.query_params.get('sortField')), reverse=False if request.query_params.get('sortOrder') == 'asc' else True)
        else:
            sorted_data = sorted(filter(lambda x: x.get('state') == 'ongoing', data), key=lambda x: x.get('start_time')) + sorted(filter(lambda x: x.get('state') != 'ongoing', data), key=lambda x: x.get('start_time'))

        return Response({
            'data': sorted_data[(page - 1) * page_size:(page) * page_size],
            'itemsCount': len(dataframe)
        })

    def get_queryset(self):
        queryset = self.queryset
        creators = self.request.query_params.get('creators')
        brand = self.request.query_params.get('brand')
        date_range = self.request.query_params.get('date_range')

        if creators:
            queryset = queryset.filter(ad__creator__in=creators.split(','))

        if brand:
            queryset = queryset.filter(ad__brand_id=brand)

        if date_range:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
            print "start date", start_date, "end date", end_date
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)

        return queryset


class AdCreatorAPIView(APIView, BaseMarketingAPIView):
    def get(self, request, *args, **kwargs):
        q = self.request.query_params.get('q')

        if q:
            queryset = Ad.objects.filter(creator__istartswith=q)
        else:
            queryset = Ad.objects.filter(creator__isnull=False)

        return Response({
            'results': queryset.distinct('creator').values_list('creator', flat=True)
        }) 


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


class AdInstallDashboadCountAPIView(APIView, BaseMarketingAPIView):
    def get(self, request, *args, **kwargs):
        counts = {}
        brand_id = request.query_params.get('brand')
        print "dashboard", request.query_params


        for item in request.query_params.get('queries').split(','):
            if brand_id:
                if item == 'ad_install_dashboard_total_installs':
                    count = AdStats.objects.filter(ad__brand_id=brand_id).aggregate(Sum('install_count')).get('install_count__sum', 0) or 0
                elif item == 'ad_install_dashboard_total_views':
                    count = AdStats.objects.filter(ad__brand_id=brand_id).aggregate(Sum('view_count')).get('view_count__sum', 0) or 0

                count = intword(count)
            else:
                count = intword(DatabaseRecordCount.get_value(item))

            count_split = count.split(' ') if not type(count) == int else []

            if len(count_split) > 1:
                count = str(int(float(count_split[0]))) + ' ' + count_split[1].capitalize()[0]

            counts[item] = count

        if brand_id:
            counts['brand_name'] = Brand.objects.get(id=brand_id).name

        return Response(counts)

class EventBookingListAPIView(ListAPIView, BaseMarketingAPIView):
    queryset = EventBooking.objects.all()
    pagination_class = deepcopy(PageNumberPaginationRemastered)
    serializer_class = EventBookingSerializer

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        page_size = self.request.query_params.get('page_size')
        state = self.request.query_params.get('state')
        creators = self.request.query_params.get('creators')
        categories = self.request.query_params.get('categories')
        date_range = self.request.query_params.get('date')
        price_range = self.request.query_params.get('price_range')

        if q:
            queryset = queryset.filter(Q(user__st__name__icontains=q) | Q(user__st__mobile_no__icontains=q) |\
                                        Q(user__email__icontains=q) | Q(event__creator__st__name__icontains=q))

        if state == 'order':
            queryset = queryset.filter(state='booked')

        if creators:
            print "Creators", creators
            queryset = queryset.filter(event__creator__in=creators.split(','))

        if categories:
            print "Categories", categories
            queryset = queryset.filter(event__category__in=categories.split(','))

        if date_range:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            print "start date", start_date, "end date", end_date
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)

        if price_range:
            start_price, end_price = price_range.split(' - ')
            queryset = queryset.filter(event__price__gte=start_price, event__price__lte=end_price)

        if page_size:
            self.pagination_class.page_size = int(page_size)

        return queryset.order_by('-created_at')

class EventCreatorListAPIView(APIView, BaseMarketingAPIView):
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q')
        queryset = Event.objects.all()

        if q:
            queryset = queryset.filter(creator__username__icontains=q)
        
        return Response({
            'results': queryset.distinct('creator_id').values('creator_id', 'creator__username')
        })

class EventCategoryListAPIView(ListAPIView, BaseMarketingAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventBookingCountsAPIView(APIView, BaseMarketingAPIView):
    def get(self, request, *args, **kwargs):
        today = datetime.now()
        start_date = today - timedelta(days=today.day-1)
        end_date = start_date + relativedelta(months=1) - timedelta(days=1)
        data = {
            'lifetime_bookings': EventBooking.objects.count(),
            'current_month_bookings': EventBooking.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).count(),
            'lifetime_revenues': EventBooking.objects.aggregate(sum_revenue=Sum('event__price')).get('sum_revenue'),
            'current_month_revenues': EventBooking.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(sum_revenue=Sum('event__price')).get('sum_revenue'),
            'order_amount_min': Event.objects.aggregate(min_price=Min('price')).get('min_price'),
            'order_amount_max': Event.objects.aggregate(max_price=Max('price')).get('max_price'),
            'current_month_name': datetime.strftime(today, '%B')
        }
        return Response(data)

class EventStatsListAPIView(ListAPIView, BaseMarketingAPIView):
    queryset = EventStats.objects.all()
    serializer_class = EventStatsSerializer
    pagination_class = deepcopy(PageNumberPaginationRemastered)

    def get_queryset(self):
        queryset = self.queryset.filter(event_id=self.kwargs.get('event_id'))
        date_range = self.request.query_params.get('date_range')

        if date_range:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
            print "start date", start_date, "end date", end_date
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)

        return queryset.order_by('-date')


class EventStatsCountsAPIView(APIView, BaseMarketingAPIView):
    def get(self, request, event_id, *args, **kwargs):
        event_queryset = EventStats.objects.filter(event_id=event_id)
        data = {
            'lifetime_bookings': event_queryset.aggregate(sum_bookings=Sum('confirm_booking_count')).get('sum_bookings'),
            'lifetime_revenues': event_queryset.aggregate(sum_revenues=Sum('total_revenue')).get('sum_revenues'),
            'lifetime_views': event_queryset.aggregate(sum_views=Sum('view_count')).get('sum_views'),
            'lifetime_clicks': event_queryset.aggregate(sum_clicks=Sum('click_count')).get('sum_clicks'),
        }
        return Response(data)


class EventStatsChartDataAPIView(APIView):
    WEEK_ENUM = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    MONTH_ENUM = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    def get(self, request, event_id, *args, **kwargs):
        chart_type = request.query_params.get('chart_type')
        data_type = request.query_params.get('data_type')
        cursor = connections['read'].cursor()
        date_range = request.query_params.get('date_range')

        if date_range:
            start_date, end_date = date_range.split(' - ')
        else:
            start_date, end_date = None, None

        result = [[], []]

        if chart_type == 'views':
            if data_type == 'daily':
                cursor.execute("""
                    select date::varchar, count
                    from (
                        select date::date, sum(view_count) as count
                        from marketing_eventstats
                        where event_id = %s
                        group by date::date
                    ) A
                """, [event_id])
                result = self.get_daily_data(self.dictfetchall(cursor))
                
            elif data_type == 'weekly':
                today = datetime.now()
                cursor.execute("""
                    select date::date::varchar, count
                    from (
                        select DATE_TRUNC('week', date) as date, sum(view_count) as count
                        from marketing_eventstats
                        where event_id = %s
                        group by DATE_TRUNC('week', date)
                    ) A
                """, [event_id])
                result = self.get_weekly_data(self.dictfetchall(cursor))

            elif data_type == 'monthly':
                today = datetime.now()
                cursor.execute("""
                    select date::date::varchar, count
                    from (
                        select DATE_TRUNC('month', date) as date, sum(view_count) as count
                        from marketing_eventstats
                        where event_id = %s
                        group by DATE_TRUNC('month', date)
                    ) A
                """, [event_id])
                result = self.get_monthly_data(self.dictfetchall(cursor))

        elif chart_type == 'bookings':
            if data_type == 'daily':
                cursor.execute("""
                    select date::varchar, count
                    from (
                        select date::date, sum(total_revenue) as count
                        from marketing_eventstats
                        where event_id = %s
                        group by date::date
                    ) A
                """, [event_id])
                result = self.get_daily_data(self.dictfetchall(cursor))
                
            elif data_type == 'weekly':
                today = datetime.now()
                cursor.execute("""
                    select date::date::varchar, count
                    from (
                        select DATE_TRUNC('week', date) as date, sum(total_revenue) as count
                        from marketing_eventstats
                        where event_id = %s
                        group by DATE_TRUNC('week', date)
                    ) A
                """, [event_id])
                result = self.get_weekly_data(self.dictfetchall(cursor))

            elif data_type == 'monthly':
                today = datetime.now()
                cursor.execute("""
                    select date::date::varchar, count
                    from (
                        select DATE_TRUNC('month', date) as date, sum(total_revenue) as count
                        from marketing_eventstats
                        where event_id = %s
                        group by DATE_TRUNC('month', date)
                    ) A
                """, [event_id])
                result = self.get_monthly_data(self.dictfetchall(cursor))

        return Response({
            'labels': result[0],
            'dataset': result[1],
        })

    def dictfetchall(self, cursor):
        return {
            row[0]: row[1] for row in cursor.fetchall()
        }

    def get_daily_data(self, query_data):
        start_date = datetime.strptime(min(query_data.keys()), '%Y-%m-%d')
        end_date = datetime.now()
        interval = (end_date - start_date).days

        labels = []
        dataset = []

        for i in range(interval+1):
            current_date = str((start_date + timedelta(i)).date())
            labels.append(current_date)
            dataset.append(query_data.get(current_date))

        return labels, dataset


    def get_weekly_data(self, query_data):
        print "query data", query_data
        start_date = datetime.strptime(min(query_data.keys()), '%Y-%m-%d')
        end_date = datetime.now()

        labels = []
        dataset = []

        current_date = start_date
        while current_date <= end_date:
            labels.append(datetime.strftime(current_date, '%d-%m-%y'))
            dataset.append(query_data.get(str(current_date.date()), 0))

            current_date += relativedelta(days=7)

        return labels, dataset

    def get_monthly_data(self, query_data):
        print "query data", query_data
        start_date = datetime.strptime(min(query_data.keys()), '%Y-%m-%d')
        end_date = datetime.now()
        end_date = datetime.strptime('%d-%d-01'%(end_date.year, end_date.month), '%Y-%m-%d')

        labels = []
        dataset = []

        current_date = start_date
        while current_date <= end_date:
            labels.append(datetime.strftime(current_date, '%B-%y'))
            dataset.append(query_data.get(str(current_date.date()), 0))

            current_date += relativedelta(months=1)

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

