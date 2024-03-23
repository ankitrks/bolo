# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
from datetime import datetime

from django.shortcuts import render
from django.views.generic import View
from django.db import connections
from django.http import HttpResponseBadRequest,HttpResponse


class DownloadView(View):
    file_name = 'report_download'
    headers = None
    default_format = 'csv'

    @property
    def complete_file_name(self):
        return self.file_name + '.' + self.request.GET.get('format', self.default_format)

    def download(self):
        rows = self.execute_query(*self.get_query_with_params())
        print "headers", self.headers
        file_type = self.request.GET.get('format', self.default_format)

        if file_type == 'csv':
            return self.prepare_csv_data(self.headers, rows, self.file_name)
        else:
            raise HttpResponseBadRequest()

    def execute_query(self, query, params=None):
        if params:
            print "query", self.cursor.mogrify(query, params)
            self.cursor.execute(query, params)
        else:
            print "query", self.cursor.mogrify(query)
            self.cursor.execute(query)
        
        if not self.headers:
            self.headers = [col[0] for col in self.cursor.description]

        return self.cursor.fetchall()

    def get_query(self):
        return ''

    def get_param_data(self):
        return []

    def get_headers(self):
        if self.headers:
            return self.headers

    def get(self, request, *args, **kwargs):
        self.cursor = connections['default'].cursor()
        response = self.download()

        if not self.cursor.closed:
            self.cursor.close()
        
        return response

    def prepare_csv_data(self, fields, rows, file_name):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s'%self.complete_file_name

        writer = csv.writer(response, quoting=csv.QUOTE_ALL)

        writer.writerow([name.encode('utf-8') for name in fields])

        for data in rows:
            row = []
            for d in data:
                if isinstance(d, unicode):
                    try:
                        d = d.encode('utf-8')
                    except UnicodeError as e:
                        print str(e)
                        pass
                if d is False: d = None

                # Spreadsheet apps tend to detect formulas on leading =, + and -
                #if type(d) is str and d.startswith(('=', '-', '+')):
                #    d = "'" + d

                row.append(d)
            writer.writerow(row)

        return response


class AdOrderDownload(DownloadView):
    file_name = 'order_details'

    def get_query_with_params(self):
        query = """
            select 
                ROW_NUMBER() OVER (ORDER BY o.id desc) as "S No", to_char(o.created_at, 'DD-MM-YYYY HH:MI:SS') as order_date, product.name as product_name, line.quantity as quantity,
                (tax.percentage/100.0 * o.amount ) + o.amount as paid_amount, o.payment_status, o.state, 
                address.name as customer_name, address.email as customer_email, address.mobile as customer_mobile, 
                concat(address.address1, ', ', address.address2, ', ', city.name, ', ', st.name, ' - ', address.pincode)  as customer_address
            from advertisement_order o
            left join auth_user u on o.user_id = u.id
            left join forum_user_userprofile profile on profile.user_id = o.user_id
            left join advertisement_orderline line on line.order_id = o.id
            left join advertisement_product product on product.id = line.product_id
            left join advertisement_brand brand on brand.id = product.brand_id
            left join advertisement_product_taxes product_tax on product_tax.product_id = product.id
            left join advertisement_tax tax on tax.id = product_tax.tax_id
            left join advertisement_address address on address.id = o.shipping_address_id
            left join advertisement_state st on st.id = address.state_id
            left join advertisement_city city on city.id = address.city_id
            where  o.state != 'draft' 
        """
        params = []

        if self.request.GET.get('payment_status'):
            query += " and o.payment_status in %s "
            params.append(tuple(self.request.GET.get('payment_status').split(',')))

        if self.request.GET.get('product_ids'):
            query += "  and product.id in %s " 
            params.append(tuple(self.request.GET.get('product_ids')))

        if self.request.GET.get('amount_range'):
            min_amount, max_amount = self.request.GET.get('amount_range').split(' - ')
            query += " and o.amount >= %s and o.amount <= %s "
            params.append(min_amount)
            params.append(max_amount)

        if self.request.GET.get('date'):
            start_date, end_date = self.request.GET.get('date').split(' - ')
            query += " and o.date between %s and %s "
            params.append(datetime.strptime(start_date, '%d-%m-%Y'))
            params.append(datetime.strptime(end_date, '%d-%m-%Y'))

        if self.request.GET.get('q'):
            query += " and (address.name ilike %s or address.mobile ilike %s or address.email ilike %s ) "
            params.append('%' + self.request.GET.get('q') + '%')
            params.append('%' + self.request.GET.get('q') + '%')
            params.append('%' + self.request.GET.get('q') + '%')

        query +=  " order by o.id desc"

        return query, params

class AdInstallStatsDownloadView(DownloadView):
    file_name = 'install_stats'

    def get_query_with_params(self):
        query = """
            select S."S No" as "Sr No", brand.name as "Brand", ad.id as "Ad Id", ad.creator as "Creator Name", S.view_count as "Views", 
                S.install_count as "Installs", 
                round(cast(float8(S.install_count)/float8(COALESCE(nullif(S.view_count, 0), 1)) as numeric), 2) * 100 as "CTR", 
                S.skip_count as "Skips",  S.full_watched as "Full Watched",
                round(cast(float8(S.install_playtime)/float8(COALESCE(nullif(S.install_count, 0), 1)) as numeric), 0) as "Avg. time before Install (Secs)", 
                round(cast(float8(S.skip_playtime)/float8(COALESCE(nullif(S.skip_count, 0), 1)) as numeric), 0) as "Avg. time before Skip (Secs)"
                from (
                select  ROW_NUMBER() OVER (ORDER BY stats.ad_id) as "S No", ad_id, sum(view_count) as view_count, 
                    sum(install_count) as install_count, sum(full_watched) as full_watched, sum(skip_count) as skip_count,
                    sum(install_playtime) as install_playtime, sum(skip_playtime) as skip_playtime
                from marketing_adstats stats
                inner join advertisement_ad ad on ad.id = stats.ad_id
                where ad.ad_type = 'install_now' and %s
                group by ad_id
                ) S
            inner join advertisement_ad ad on ad.id = S.ad_id
            inner join advertisement_brand brand on brand.id = ad.brand_id
            inner join auth_user u on u.id = ad.created_by_id
            where true
        """
        params = []

        if self.request.GET.get('date_range'):
            start_date, end_date = self.request.GET.get('date_range').split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
            print "date ragnge", " date between '%s' and '%s' "%(datetime.strftime(start_date, '%Y-%m-%d'), datetime.strftime(end_date, '%Y-%m-%d'))
            query = query%" date between '%s' and '%s' "%(datetime.strftime(start_date, '%Y-%m-%d'), datetime.strftime(end_date, '%Y-%m-%d'))
            
        else:
            query = query%"true"

        if self.request.GET.get('creators'):
            query += " and ad.creator in %s "
            params.append(tuple(self.request.GET.get('creators').split(',')))

        if self.request.GET.get('brand'):
            query += "  and ad.brand_id = %s " 
            params.append(int(self.request.GET.get('brand')))


        # if self.request.GET.get('q'):
        #     query += " and (address.name ilike %s or address.mobile ilike %s or address.email ilike %s ) "
        #     params.append('%' + self.request.GET.get('q') + '%')
        #     params.append('%' + self.request.GET.get('q') + '%')
        #     params.append('%' + self.request.GET.get('q') + '%')

        query +=  " order by ad.id "

        return query, params



class EventBookingStatsDownloadView(DownloadView):
    file_name = 'install_stats'

    def get_query_with_params(self):
        query = """
            select  booker_profile.name as "Name", 
                    booker_profile.mobile_no as "Phone Number", booker.email as "Email Id", e.price as "Amount Paid",
                    creator_profile.name as "Creator Name", creator.username as "Creator UserName", 
                    e.title as "Event Title", category.title as "Category",
                    booking.created_at::date as "Order Date", booking.state as "Status"
            from booking_eventbooking booking
            left join booking_event e on booking.event_id = e.id
            left join auth_user booker on booker.id = booking.user_id
            left join forum_user_userprofile booker_profile on booker_profile.user_id = booking.user_id
            left join auth_user creator on creator.id = e.creator_id
            left join forum_user_userprofile creator_profile on creator_profile.user_id = e.creator_id
            left join forum_category_category category on category.id = e.category_id
            where true
        """
        params = []

        if self.request.GET.get('state') == 'order':
            query += " and booking.state = 'booked' "

        if self.request.GET.get('date'):
            start_date, end_date = self.request.GET.get('date').split(' - ')
            start_date = datetime.strptime(start_date, '%d-%m-%Y')
            end_date = datetime.strptime(end_date, '%d-%m-%Y')
            print "date ragnge", " date between '%s' and '%s' "%(datetime.strftime(start_date, '%Y-%m-%d'), datetime.strftime(end_date, '%Y-%m-%d'))
            query += " and booking.created_at between '%s' and '%s' "%(datetime.strftime(start_date, '%Y-%m-%d'), datetime.strftime(end_date, '%Y-%m-%d'))


        if self.request.GET.get('creators'):
            query += " and e.creator_id in %s "
            params.append(tuple(self.request.GET.get('creators').split(',')))

        if self.request.GET.get('categories'):
            query += "  and e.category_id in %s " 
            params.append(tuple(self.request.GET.get('categories').split(',')))


        if self.request.GET.get('price_range'):
            min_price, max_price = self.request.GET.get('price_range').split(' - ')
            query += " and e.price between %s and %s "
            params.append(int(min_price))
            params.append(int(max_price))

        if self.request.GET.get('q'):
            query += " and (booker_profile.name ilike %s or booker_profile.mobile_no ilike %s or booker.email ilike %s or creator_profile.name ilike %s ) "
            params.append('%' + self.request.GET.get('q') + '%')
            params.append('%' + self.request.GET.get('q') + '%')
            params.append('%' + self.request.GET.get('q') + '%')
            params.append('%' + self.request.GET.get('q') + '%')

        query +=  " order by booking.created_at desc "

        return query, params

    def prepare_csv_data(self, fields, rows, file_name):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s'%self.complete_file_name

        writer = csv.writer(response, quoting=csv.QUOTE_ALL)

        writer.writerow([name.encode('utf-8') for name in fields])

        for i, data in enumerate(rows):
            row = []
            for d in data:
                if isinstance(d, unicode):
                    try:
                        d = d.encode('utf-8')
                    except UnicodeError as e:
                        print str(e)
                        pass
                if d is False: d = None

                # Spreadsheet apps tend to detect formulas on leading =, + and -
                #if type(d) is str and d.startswith(('=', '-', '+')):
                #    d = "'" + d

                row.append(d)
            row.insert(0, i+1)
            writer.writerow(row)

        return response