from django.conf.urls import include, url
from .views import login, get_user_data

urlpatterns = [
    url(r'login', login, name='login'),
    url(r'user', get_user_data, name='user'),
]
