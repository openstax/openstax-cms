from django.urls import re_path
from .views import accounts

urlpatterns = [
    re_path(r"^.*$", accounts),
]
