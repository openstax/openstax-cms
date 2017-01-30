from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.ErrataView, base_name='errata')

urlpatterns = [
    url(r'^', include(router.urls)),
]
