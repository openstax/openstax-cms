from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.ErratumView, base_name='erratum')

urlpatterns = [
    url(r'^(?P<id>\d+)/$', views.errata_detail),
] + router.urls
