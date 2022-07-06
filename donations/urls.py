from django.urls import include, path
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'donation-popup', views.DonationPopupViewSet, basename='DonationPopup')
router.register(r'fundraiser', views.FundraiserViewSet, basename='Fundraiser')

urlpatterns = [
    path('', include(router.urls)),
    path('thankyounote/', views.ThankYouNoteViewSet.as_view({'post': 'post'}))
]
