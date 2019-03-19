from django.conf.urls import include, url
from .views import login, logout, get_user_data

urlpatterns = [
    url(r'login', login, name='login'),
    url(r'logout', logout, name='logout'),
    url(r'user', get_user_data, name='user'),
]
