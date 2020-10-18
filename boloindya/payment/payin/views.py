# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from payment.razorpay import get_order, is_signature_verified
from payment.helpers import get_user_info, get_booking_info

KEY = "rzp_test_CRX59NwqZqFS8P"

class RazorpayPaymentView(TemplateView):
    template_name = 'payment/payin/booking_payment.html'

    def get(self, request, booking_id, *args, **kargs):
        self.booking_id = booking_id
        return super(RazorpayPaymentView, self).get(request, order_id, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CustomerPaymentView, self).get_context_data(**kwargs)
        context['key'] = KEY
        booking_info = get_booking_info(booking_id)
        context['order'] = get_order(booking_info.get('payment_gateway_order_id'))
        print("booking_info", booking_info)
        context['user'] = get_user_info(booking_info.get('user_id'))
        context['amount'] = booking_info.get('amount')
        context['type'] = self.request.GET.get('type')
        return context


class RazorpayCallbackView(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CustomerPaymentResponseView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST
        if is_signature_verified(data.get('razorpay_order_id'), data.get('razorpay_payment_id'), data.get('razorpay_signature')):
            update_payment_status(True)
        else:
            update_payment_status(False)
