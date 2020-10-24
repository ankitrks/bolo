
from collections import OrderedDict, namedtuple


from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationRemastered(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('itemsCount', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))