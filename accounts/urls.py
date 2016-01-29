from django.conf.urls import patterns, url, include
from rest_framework import routers
 
from accounts.user_api import views
 
router = routers.DefaultRouter()
router.register(r'user', views.UserView, 'user')
 
urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
