from django.conf.urls import include, url
from .views import logout, login

urlpatterns = [
    url(r"^/login/?$", login, name="login"),
    url(r"^/logout/?$", logout, name="logout"),
]
