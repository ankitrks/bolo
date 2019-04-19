from django.conf.urls import url, include
from django.contrib import admin

from drf_spirit import urls 

urlpatterns = [
    url(r'^', include(urls))
]
