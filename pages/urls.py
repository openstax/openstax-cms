from django.urls import path

from pages.admin_views import TablePreviewView

urlpatterns = [
    path('preview/', TablePreviewView.as_view(), name='table_block_preview'),
]
