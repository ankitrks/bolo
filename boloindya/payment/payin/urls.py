from django.conf.urls import include, url
from payment.payin.views import RazorpayPaymentView, RazorpayCallbackView, RazorpayWebhookView, PaymentFaliureView

urlpatterns = [
    url(r'^razorpay/(?P<order_id>[\w_]+)/pay$', RazorpayPaymentView.as_view()),
    url(r'^razorpay/callback$', RazorpayCallbackView.as_view()),
    url(r'^razorpay/webhook$', RazorpayWebhookView.as_view()),
    url(r'^payment_failed$', PaymentFaliureView.as_view()),
]
