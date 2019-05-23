from django.conf import settings
from django.conf.urls import url

from wagtailimportexport import views


app_name = 'wagtailimportexport'
urlpatterns = [
    url(r'^export/(?P<page_id>\d+)/$', views.export, name='export'),
]

if getattr(settings, "WAGTAILIMPORTEXPORT_EXPORT_UNPUBLISHED", False):
    urlpatterns += urlpatterns + [
        url(r'^export/(?P<page_id>\d+)/all/$', views.export, {'export_unpublished': True}, name='export'),
    ]
