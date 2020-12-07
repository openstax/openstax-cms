from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'schools', views.SchoolViewSet, basename='School')
router.register(r'partners', views.PartnerViewSet, basename='Partner')
router.register(r'forms', views.SalesforceFormsViewSet, basename='Forms')
router.register(r'savings', views.SavingsNumberViewSet, basename='SavingsNumber')
router.register(r'download-tracking', views.ResourceDownloadViewSet, basename='DownloadTracking')

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^adoption-status/', views.get_adoption_status),
    url(r'renewal/(?P<account_id>\d+)/', views.AdoptionOpportunityRecordViewSet.as_view({'get': 'list', 'post': 'post'})),
    url(r'reviews/', views.PartnerReviewViewSet.as_view({'get': 'list', 'post': 'post', 'patch': 'patch', 'delete': 'delete'})),
]
