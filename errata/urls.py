from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'', views.ErrataView)

urlpatterns = [
    path('admin/dashboard/', views.dashboard, name='errata_dashboard'),
    path('admin/list/', views.list, name='errata_list'),
    path('admin/edit/', views.edit, name='errata_edit'),
    path(r'', include(router.urls)),
]
