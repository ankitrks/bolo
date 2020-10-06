from django.conf.urls import include, url

from rest_framework import routers

from payment.partner.views import BeneficiaryViewSet, TopUserListView

router = routers.SimpleRouter()

router.register('beneficiary', BeneficiaryViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^top-user$', TopUserListView.as_view())
]

