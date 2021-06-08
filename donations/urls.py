from django.conf.urls import include, url
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'donation-popup', views.DonationPopupViewSet, basename='DonationPopup')

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'thankyounote', views.ThankYouNoteViewSet.as_view({'post': 'post'}))
]
