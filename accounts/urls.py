from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^logout/', views.logout),
]
