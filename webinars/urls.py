from django.urls import include, path
#from rest_framework import routers
from . import views

#router = routers.SimpleRouter()
#router.register(r'webinars', views.WebinarViewSet, basename='Webinars')
from .search import search

urlpatterns = [
    #path(r'', include(router.urls)),
    path('webinars/', views.WebinarViewSet.as_view({'get': 'list'})),
    path('webinars/search/', search, name='webinar_search')
]
