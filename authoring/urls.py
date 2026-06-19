from django.urls import path

from authoring.views import FlexPageDraftView, FlexPageExportView

urlpatterns = [
    path('', FlexPageDraftView.as_view(), name='flex-draft-create'),
    path('<int:page_id>/export/', FlexPageExportView.as_view(), name='flex-export'),
    path('<int:page_id>/', FlexPageDraftView.as_view(), name='flex-draft-update'),
]
