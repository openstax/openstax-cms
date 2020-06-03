from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^/send_mail/?$', views.send_contact_message),
]
