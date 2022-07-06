from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^news/?$', views.news_index),
    re_path(r'^news/(?P<slug>[\w-]+)/?$', views.news_detail),

    re_path(r'^press/?$', views.press_index),
    re_path(r'^press/(?P<slug>[\w-]+)/?$', views.press_detail),
]
