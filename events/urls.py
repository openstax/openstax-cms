from django.urls import include, path
from rest_framework import routers

from .views import SessionViewSet, RegistrationViewSet, check_reg_status

router = routers.DefaultRouter()
router.register(r'sessions', SessionViewSet)
router.register(r'registration', RegistrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check/', check_reg_status, name='check_reg_status'),
]

