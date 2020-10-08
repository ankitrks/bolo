from rest_framework import permissions

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class UserPaymentPermissionView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated() and self.request.user.groups.filter(name='payment_user').exists()

    def get_login_url(self):
        if not self.request.user.is_authenticated():
            return super(UserPaymentPermissionView, self).get_login_url()
        else:
            return '/jarvis/'



class PaymentPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """
    message = "Not allowed"

    def has_permission(self, request, view):
        return request.user.is_authenticated() and request.user.groups.filter(name='payment_user').exists()