from django.conf.urls import include, url


urlpatterns = [
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
