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
                o.id, order_number, to_char(o.created_at, 'DD-MM-YYYY HH:MI:SS') as order_date, brand.name as brand_name, product.name as product_name, line.quantity as quantity,
                o.amount as order_amount, (tax.percentage/100.0 * o.amount ) + o.amount as paid_amount, o.payment_status, o.state, 
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
            where true 
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


        query +=  " order by o.created_at"

        return query, params
