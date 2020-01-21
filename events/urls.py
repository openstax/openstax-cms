from django.conf.urls import include, url
from rest_framework import routers

from .views import SessionViewSet, check_reg_status

router = routers.DefaultRouter()
router.register(r'sessions', SessionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^check/$', check_reg_status, name='check_reg_status'),
]

