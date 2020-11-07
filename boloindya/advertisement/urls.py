from django.conf.urls import include, url
from .views import AdevertisementCallView, brand_onboard_form, ad_creation_form, product_onboard_form

urlpatterns = [
	url(r'^$', AdevertisementCallView.as_view()),
	url(r'^brand/onboard/$',brand_onboard_form),
	url(r'product/onboard/$',product_onboard_form),
	url(r'^create_ad/$',ad_creation_form)
]
