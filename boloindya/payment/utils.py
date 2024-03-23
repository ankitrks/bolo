import logging

from collections import OrderedDict, namedtuple

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from tasks import send_mail_to_payout_admins

payment_logger = logging.getLogger('payment_log')
transaction_logger = logging.getLogger('transaction_log')

class PageNumberPaginationRemastered(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('itemsCount', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))

def log_message(message, title=None, log_type='info', send_mail=False):
    if log_type == 'info':
        logger = payment_logger
    elif log_type == 'transaction':
        logger = transaction_logger

    if title:
        logger.info(title + ':' + message)
    else:
        logger.info(message)

    if send_mail:
        send_mail_to_payout_admins.delay(message, title)