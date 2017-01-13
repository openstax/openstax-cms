from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^$', views.news_index),
    url(r'^(?P<id>\d+)/$', views.errata_detail),
]
