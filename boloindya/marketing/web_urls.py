from django.conf.urls import include, url
from django.contrib.admin.views.decorators import staff_member_required

from .web_views import AdStatsDashboardView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetMailView

urlpatterns = [
    url(r'^login/', LoginView.as_view()),
    url(r'^logout/', LogoutView.as_view()),
    url(r'^reset-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view()),
    url(r'^send-reset-password-mail/$', PasswordResetMailView.as_view()),
    url(r'^ad/install/stats/$', staff_member_required(AdStatsDashboardView.as_view(), login_url='/marketing/login/')),
]
