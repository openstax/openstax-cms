from django.conf.urls import url
from pages import views

urlpatterns = [
    url(r'^pages/$', views.page_list),
    url(r'^pages/(?P<slug>[\w-]+)/$', views.page_detail),
]