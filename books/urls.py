from django.urls import re_path, path
from . import views

urlpatterns = [
    path('/resources/', views.ResourcesViewSet.as_view({'get': 'list'})),
    re_path(r'^/?$', views.book_index),
    re_path(r'^/(?P<slug>[\w-]+)/?$', views.book_detail),
]
