from django.conf.urls import include, url
from django.contrib.admin.views.decorators import staff_member_required

from .views import AdevertisementCallView, brand_onboard_form, ad_creation_form, product_onboard_form, search_fields_for_advertisement, brand_management, product_management, particular_ad
from .views import OrderPaymentRedirectView, OrderTemplateView, AdTemplateView, ProductTemplateView, OrderDashboardLogin

urlpatterns = [
    url(r'^brand/onboard/$', staff_member_required(brand_onboard_form)),
    url(r'product/onboard/$', staff_member_required(product_onboard_form)),
    url(r'^onboard/$', staff_member_required(ad_creation_form)),
    url(r'^search_fields_for_ad/$', staff_member_required( search_fields_for_advertisement)),
    url(r'^order/(?P<order_id>[\d]+)/pay/$', OrderPaymentRedirectView.as_view()),
    url(r'^brand/onboard/admin/$', staff_member_required(brand_management)),
    url(r'^product/onboard/admin/$', staff_member_required(product_management)),
    url(r'^edit/(?P<ad_id>\d+)$', staff_member_required( particular_ad)),
    url(r'^$', staff_member_required( AdTemplateView.as_view())),
    url(r'^order/$', staff_member_required( OrderTemplateView.as_view())),
    url(r'^product/$', staff_member_required( ProductTemplateView.as_view())),
    url(r'^login/$', OrderDashboardLogin.as_view()),
]
