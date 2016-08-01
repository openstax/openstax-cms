from django.conf.urls import url
from pages import views

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', views.page_detail),
]
