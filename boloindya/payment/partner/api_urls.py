from django.conf.urls import include, url

from rest_framework import routers

from payment.partner.views import BeneficiaryViewSet, BeneficiaryBulkCreateAPIView

router = routers.SimpleRouter()

router.register('beneficiary', BeneficiaryViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^beneficiary/bulk_create$', BeneficiaryBulkCreateAPIView.as_view())
]


