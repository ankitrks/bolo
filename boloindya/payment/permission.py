from rest_framework import permissions

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.http import HttpResponseForbidden

from redis_utils import get_redis, set_redis

class UserPaymentPermissionView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.is_authenticated() and self.has_group_permission() and self.has_otp_session()

    def get_login_url(self):
        if not self.is_authenticated():
            return super(UserPaymentPermissionView, self).get_login_url()
        elif not self.has_group_permission():
            return HttpResponseForbidden()
        elif not self.has_otp_session():
            return '/payment/otp-verification'


    def has_group_permission(self):
        return self.request.user.groups.filter(name='payment_user').exists()

    def has_otp_session(self):
        return get_redis(settings.PAYMENT_SESSION_KEY%(self.request.user.id))

    def is_authenticated(self):
        return self.request.user.is_authenticated()

class PaymentPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """
    message = "Not Authorized"

    def has_permission(self, request, view):
        if not request.user.is_authenticated() or not request.user.groups.filter(name='payment_user').exists():
            return False

        elif not get_redis(settings.PAYMENT_SESSION_KEY%(request.user.id)):
            self.message = "Payment session expired. Please refresh the page & Enter OTP."
            return False

        return True
