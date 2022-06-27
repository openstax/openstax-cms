from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.WebinarViewSet, basename='Webinars')

urlpatterns = [
    path(r'', include(router.urls)),
]
