from django.conf.urls import url
from .views import accounts

urlpatterns = [
    url(r"^.*$", accounts),
]
