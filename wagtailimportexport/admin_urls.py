from django.conf.urls import url

from wagtailimportexport import views


app_name = 'wagtailimportexport_admin'
urlpatterns = [
    url(r'^import_from_api/$', views.import_from_api, name='import_from_api'),
    url(r'^import_from_file/$', views.import_from_file, name='import_from_file'),
    url(r'^export_to_file/$', views.export_to_file, name='export_to_file'),
    url(r'^$', views.index, name='index'),
]
