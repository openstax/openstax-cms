from django.urls import include, path
from rest_framework import routers

from .views import AdopterViewSet, ImageViewSet, DocumentViewSet, customize_request, sticky_note, footer, schools, mapbox, flags, errata_fields, give_today, webview_settings

router = routers.DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'adopters', AdopterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sticky/', sticky_note, name='sticky_note'),
    path('footer/', footer, name='footer'),
    path('schools/', schools, name='schools'),
    path('mapbox/', mapbox, name='mapbox'),
    path('flags/', flags, name='flags'),
    path('errata-fields/', errata_fields, name='errata-fields'),
    path('give-today/', give_today, name='give_today'),
    path('webview-settings/', webview_settings, name='webview_settings'),
    path('customize/', customize_request),
]

