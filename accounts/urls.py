from django.conf.urls import url, include

urlpatterns = [
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
