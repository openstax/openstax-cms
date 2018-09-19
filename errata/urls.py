from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.ErrataView)

urlpatterns = [
    url(r'^admin/dashboard/$', views.dashboard),
    url(r'^admin/list/$', views.list),
    url(r'^admin/edit/$', views.edit),
    url(r'^', include(router.urls)),
]
