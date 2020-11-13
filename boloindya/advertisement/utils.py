from django.db import connections

from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def query_fetch_data(query, params=None):
    cursor = connections['default'].cursor()
    
    if not params:
        params = []

    print "query", cursor.mogrify(query, params)
    cursor.execute(query, params)
    return dictfetchall(cursor)


def convert_to_dict_format(item):
    _dict = {}
    for key, val in item.iteritems():
        key_parts = key.split('__', 1)

        if len(key_parts) == 2:
            if _dict.get(key_parts[0]):
                _dict[key_parts[0]].update({key_parts[1]: val})
            else:
                _dict[key_parts[0]] = {key_parts[1]: val}
        elif len(key_parts) == 1:
            _dict[key_parts[0]] = val


    for key, val in _dict.iteritems():
        if type(val) == dict:
            _dict[key] = convert_to_dict_format(val)

    return _dict


def filter_data_from_dict(keys, _dict):
    new_dict = {}

    for key in keys:
        if _dict.get(key):
            new_dict[key] = _dict.get(key)

    return new_dict

class PageNumberPaginationRemastered(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('itemsCount', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))

CTA_OPTIONS = {
    'install_now': 'Install Now',
    'learn_more': 'Learn More',
    'shop_now': 'Shop Now',
    'skip': 'Skip'
}