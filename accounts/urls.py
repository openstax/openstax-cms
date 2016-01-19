from django.conf.urls import patterns, url, include
from rest_framework import routers
from accounts.user_api import views

router = routers.DefaultRouter()
router.register(r'user', views.UserView, 'user')
 
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^$', 'accounts.views.home'),
    url(r'^login/$', 'accounts.views.login',name='login'),
    url(r'^logout/$', 'accounts.views.logout',name='logout'),
    url(r'^done/$', 'accounts.views.done', name='done'),
    url(r'^profile/$', 'accounts.views.profile', name='profile'),
    url(r'^oauth/$', 'accounts.views.oauth',name='oauth'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
)
