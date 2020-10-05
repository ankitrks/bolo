from django.conf.urls import include, url

from bipayments.partner.views import BeneficiaryTemplateView, BeneficiaryDetailTemplateView, TopUserTemplateView

urlpatterns = [
    url('beneficiary', BeneficiaryTemplateView.as_view(), name='beneficiary'),
    url('beneficiary/<int:pk>', BeneficiaryDetailTemplateView.as_view(), name='beneficiary-view'),
    url('top-users', TopUserTemplateView.as_view(), name='top_users'),
]
