from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.errata_list),
    url(r'^(?P<id>\d+)/$', views.errata_detail),
]
