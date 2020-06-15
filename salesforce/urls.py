from django.conf.urls import include, url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'schools', views.SchoolViewSet, basename='School')
router.register(r'renewal', views.AdoptionOpportunityRecordViewSet, basename='AdoptionOpportunityRecord')
router.register(r'partners', views.PartnerViewSet, basename='Partner')
router.register(r'forms', views.SalesforceFormsViewSet, basename='Forms')

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^adoption-status/', views.get_adoption_status),
    url(r'^renewal/update/(?P<account_id>\d+)', views.AdoptionUpdated.as_view(), name='adoption-updated'),
]
