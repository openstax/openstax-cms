from django.conf.urls import include, url
from rest_framework import routers

from .views import SessionViewSet, eventbrite

router = routers.DefaultRouter()
router.register(r'sessions', SessionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^eventbrite/$', eventbrite, name='eventbrite'),
]

