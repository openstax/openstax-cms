from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', views.login,name='login'),
    url(r'^logout/$', views.logout,name='logout'),
    url(r'^done/$', views.done, name='done'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^auth/$', views.auth,name='auth'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
