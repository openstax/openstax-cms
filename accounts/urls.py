from django.conf.urls import include, url

urlpatterns = [
    url(r'', include('social_django.urls', namespace='social')),
]
