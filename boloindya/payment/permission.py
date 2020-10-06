from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class UserPaymentPermissionView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        print "is authenticated", self.request.user.is_authenticated()
        print "groups", self.request.user.groups.filter(name='payment_user')
        return self.request.user.is_authenticated() and self.request.user.groups.filter(name='payment_user').exists()

    def get_login_url(self):
        if not self.request.user.is_authenticated():
            return super(UserPaymentPermissionView, self).get_login_url()
        else:
            return '/jarvis/'