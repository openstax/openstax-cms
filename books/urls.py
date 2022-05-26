from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^/?$', views.book_index),
    re_path(r'^/(?P<slug>[\w-]+)/?$', views.book_detail),
]
