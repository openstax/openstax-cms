from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'roles', views.RoleViewSet, base_name='roles')
router.register(r'version', views.VersionViewSet, base_name='version')
urlpatterns = router.urls

