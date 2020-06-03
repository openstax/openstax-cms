from django.conf.urls import include, url
from django.urls import re_path
from rest_framework import routers

from .views import SessionViewSet, RegistrationViewSet, check_reg_status

router = routers.DefaultRouter()
router.register(r'sessions', SessionViewSet)
router.register(r'registration', RegistrationViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    re_path(r'^check/?$', check_reg_status, name='check_reg_status'),
]
