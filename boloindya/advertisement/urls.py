from django.conf.urls import include, url
from .views import AdevertisementCallView, brand_onboard_form, ad_creation_form, product_onboard_form, search_fields_for_advertisement, brand_management, product_management, particular_ad
from .views import OrderPaymentRedirectView

urlpatterns = [
    url(r'^$', AdevertisementCallView.as_view()),
    url(r'^brand/onboard/$',brand_onboard_form),
    url(r'product/onboard/$',product_onboard_form),
    url(r'^create/$',ad_creation_form),
    url(r'^search_fields_for_ad/$', search_fields_for_advertisement),
    url(r'^order/(?P<order_id>[\d]+)/pay/$', OrderPaymentRedirectView.as_view()),
    url(r'^brand/onboard/admin/$',brand_management),
    url(r'^product/onboard/admin/$',product_management),
    url(r'^edit/(?P<ad_id>\d+)$', particular_ad)
]
