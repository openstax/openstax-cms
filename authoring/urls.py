from django.urls import path

from authoring.views import FlexPageDraftView

urlpatterns = [
    path('', FlexPageDraftView.as_view(), name='flex-draft-create'),
    path('<int:page_id>/', FlexPageDraftView.as_view(), name='flex-draft-update'),
]
