from django.conf.urls import include, url
from rest_framework import routers

from .views import AdopterViewSet, ImageViewSet, UserView, sf_update

router = routers.DefaultRouter()
router.register(r'v0/images', ImageViewSet)
router.register(r'user', UserView, 'user')
router.register(r'adopters', AdopterViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^sf_update/$', sf_update, name='sf_update'),
]

