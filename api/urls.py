from django.conf.urls import include, url
from rest_framework import routers

from .views import AdopterViewSet, ImageViewSet, DocumentViewSet, user_salesforce_update, user_api, sticky_note, footer

router = routers.DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'adopters', AdopterViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^user_salesforce/$', user_salesforce_update, name='user_salesforce'),
    url(r'^user/$', user_api, name='user_api'),
    url(r'^sticky/$', sticky_note, name='sticky_note'),
    url(r'^footer/$', footer, name='footer'),
]

