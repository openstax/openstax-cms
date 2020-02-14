from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'webinars', views.WebinarViewSet, basename='Webinars')

urlpatterns = [
    url(r'', include(router.urls)),
]
