from django.conf.urls import include, url
from .views import AdevertisementCallView, brand_onboard_form, ad_creation_form, product_onboard_form, search_fields_for_advertisement

urlpatterns = [
	url(r'^$', AdevertisementCallView.as_view()),
	url(r'^brand/onboard/$',brand_onboard_form),
	url(r'product/onboard/$',product_onboard_form),
	url(r'^create/ad/$',ad_creation_form),
	url(r'^search_fields_for_ad/$', search_fields_for_advertisement)
]
