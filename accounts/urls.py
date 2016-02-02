from django.conf.urls import url, include


urlpatterns = [
    url(r'^$', 'accounts.views.home'),
    url(r'^login/$', 'accounts.views.login',name='login'),
    url(r'^logout/$', 'accounts.views.logout',name='logout'),
    url(r'^done/$', 'accounts.views.done', name='done'),
    url(r'^profile/$', 'accounts.views.profile', name='profile'),
    url(r'^auth/$', 'accounts.views.auth',name='auth'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
