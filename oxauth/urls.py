from django.urls import include, path
from .views import logout, login

urlpatterns = [
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]
