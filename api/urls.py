from django.conf.urls import include, url
from django.urls import re_path
from rest_framework import routers

from .views import AdopterViewSet, ImageViewSet, DocumentViewSet, ProgressViewSet, sticky_note, footer, schools, mapbox, flags, errata_fields

router = routers.DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'adopters', AdopterViewSet)
router.register(r'progress', ProgressViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^sticky/?$', sticky_note, name='sticky_note'),
    re_path(r'^footer/?$', footer, name='footer'),
    re_path(r'^schools/?$', schools, name='schools'),
    re_path(r'^mapbox/?$', mapbox, name='mapbox'),
    re_path(r'^flags/?$', flags, name='flags'),
    re_path(r'^errata-fields/?$', errata_fields, name='errata-fields'),
]

