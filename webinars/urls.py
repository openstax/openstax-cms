from django.urls import include, path
from rest_framework import routers
from . import views
from .search import search

router = routers.SimpleRouter()
router.register(r'', views.WebinarViewSet, basename='Webinars')

urlpatterns = [
    path('search/', search, name='webinar_search'),
    path(r'', include(router.urls)),
]
