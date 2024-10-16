from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'schools', views.SchoolViewSet, basename='School')
router.register(r'partners', views.PartnerViewSet, basename='Partner')
router.register(r'forms', views.SalesforceFormsViewSet, basename='Forms')
router.register(r'savings', views.SavingsNumberViewSet, basename='SavingsNumber')
router.register(r'download-tracking', views.ResourceDownloadViewSet, basename='DownloadTracking')

urlpatterns = [
    path('', include(router.urls)),
    #TODO: remove
    path('reviews/', views.AdoptionOpportunityRecordViewSet.as_view({'get': 'list'})),
    path('renewal/', views.AdoptionOpportunityRecordViewSet.as_view({'get': 'list'})),

]
