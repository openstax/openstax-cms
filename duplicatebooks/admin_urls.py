from django.urls import path

from duplicatebooks import views


app_name = 'duplicatebooks_admin'
urlpatterns = [
    path(r'do/<page>/', views.duplicate, name='duplicate'),
]
