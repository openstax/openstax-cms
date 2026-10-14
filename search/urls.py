from django.urls import path

from .views import SearchView

urlpatterns = [
    path('', SearchView.as_view(), name='search-v2'),
]
