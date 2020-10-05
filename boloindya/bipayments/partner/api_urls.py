from django.conf.urls import include, url

from rest_framework import routers

from bipayments.partner.views import BeneficiaryViewSet, TopUserListView

router = routers.SimpleRouter()

router.register('beneficiary', BeneficiaryViewSet)

urlpatterns = router.urls

urlpatterns += [
    url('top-user', TopUserListView.as_view())
]

