from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/news/?$', views.news_index),
    url(r'^/news/(?P<slug>[\w-]+)/?$', views.news_detail),

    url(r'^/press/?$', views.press_index),
    url(r'^/press/(?P<slug>[\w-]+)/?$', views.press_detail),
]
