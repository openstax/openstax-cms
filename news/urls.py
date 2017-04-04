from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^$', views.news_index),
    url(r'^(?P<slug>[\w-]+)/$', views.news_detail),
]
