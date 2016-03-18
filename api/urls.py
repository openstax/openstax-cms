from django.conf.urls import include, url
from rest_framework import routers
from .views import ImageViewSet, UserView, AdopterViewSet  


router = routers.DefaultRouter()
router.register(r'v0/images', ImageViewSet)
router.register(r'user', UserView, 'user')
router.register(r'salesforce/adopters', AdopterViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]

