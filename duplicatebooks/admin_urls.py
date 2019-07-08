from django.conf.urls import url

from duplicatebooks import views


app_name = 'duplicatebooks_admin'
urlpatterns = [
    url(r'^do/(?P<page>[\w-]+)/?$', views.duplicate, name='duplicate'),
]
