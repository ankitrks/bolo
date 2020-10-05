"""payment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from django.contrib import admin
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/payment/partner/top-users'), name='home'),
    url('admin/', admin.site.urls),
    url('payout/', include('payment.payout.urls')),
    url('partner/', include('payment.partner.urls')),
]


if settings.DEBUG :
    urlpatterns += static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)


print urlpatterns
