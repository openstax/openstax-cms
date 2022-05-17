from django.urls import re_path

from wagtailimportexport import views


app_name = 'wagtailimportexport'
urlpatterns = [
    re_path(r'^import-page/$', views.import_page, name='import-page'),
    re_path(r'^export-page/$', views.export_page, name='export-page'),
    re_path(r'^$', views.index, name='index'),
]
