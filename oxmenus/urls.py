from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.OXMenusViewSet, basename='OXMenus')

urlpatterns = [
    path(r'', include(router.urls)),
]