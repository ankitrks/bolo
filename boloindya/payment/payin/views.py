# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from payment.razorpay import get_order, is_signature_verified
from payment.helpers import get_user_info, get_booking_info, update_booking_payment_status

razorpay_credentials = settings.RAZORPAY

class RazorpayPaymentView(TemplateView):
    template_name = 'payment/payin/booking_payment.html'

    def get_context_data(self, **kwargs):
        context = super(RazorpayPaymentView, self).get_context_data(**kwargs)
        context['key'] = razorpay_credentials.get('USERNAME')
        context['callback_url'] = "https://" + self.request.META.get('HTTP_HOST') + "/payment/razorpay/callback?type=%s"%self.request.GET.get('type')
        if self.request.GET.get('type') == 'booking':
            booking_info = get_booking_info(self.request.resolver_match.kwargs.get('order_id'))
            if booking_info:
                booking_info = booking_info[0]
            print("booking_info", booking_info)
            context['order'] = get_order(booking_info.get('order_id'))
            
            context['name'] = booking_info.get('name')
            context['email'] = booking_info.get('email')
            context['mobile'] = booking_info.get('mobile')
            
        return context


class RazorpayCallbackView(TemplateView):
    template_name = 'payment/payin/payment_success.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(RazorpayCallbackView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        print "request get data", request.GET
        print "request post,data", request.POST
        data = request.POST
        if is_signature_verified(data.get('razorpay_order_id'), data.get('razorpay_payment_id'), data.get('razorpay_signature')):
            if self.request.GET.get('type') == 'booking':
                update_booking_payment_status(data.get('razorpay_order_id'), 'success', data.get('razorpay_payment_id'))
                return self.render_to_response({})

    def get_context_data(self, **kwargs):
        context = super(RazorpayCallbackView, self).get_context_data(**kwargs)
        context["booking_deeplink_url"] = "https://" + self.request.META.get('HTTP_HOST') + "/bookings/"
        return context
    


class RazorpayWebhookView(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(RazorpayCallbackView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        print "request get data", request.GET
        print "request post,data", request.POST