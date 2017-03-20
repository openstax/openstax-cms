from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^user_location/', views.user_location),
    url(r'^calculate_taxes/(\d+)', views.calculate_taxes),
    url(r'^tax_rate/(?P<zip>[0-9]{5})', views.tax_rate),
]
