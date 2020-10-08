from django.conf.urls import include, url
from django.contrib.auth.decorators import user_passes_test

from payment.partner.views import BeneficiaryTemplateView, BeneficiaryDetailTemplateView

urlpatterns = [
    url(r'^beneficiary$', BeneficiaryTemplateView.as_view(), name='beneficiary'),
    url(r'^beneficiary/(?P<pk>\d+)$', BeneficiaryDetailTemplateView.as_view(), name='beneficiary-view'),
]
