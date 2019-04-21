from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/?$', views.book_index),
    url(r'^/(?P<slug>[\w-]+)/?$', views.book_detail),
]
