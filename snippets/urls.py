from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.RoleViewSet)

urlpatterns = [
    url(r'^roles/', include(router.urls)),
]
