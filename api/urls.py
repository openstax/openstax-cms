from django.conf.urls import include, url
from rest_framework import routers
from .views import ImageViewSet, UserView, PageViewSet, DocumentViewSet  


router = routers.DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'user', UserView, 'user')
router.register(r'pages', PageViewSet)
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    url(r'^v0/', include(router.urls)),
]

