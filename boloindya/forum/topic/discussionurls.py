
from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.ques_ans_index, name='discussion_index'),
]