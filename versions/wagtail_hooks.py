from django.urls import path
from django.urls import reverse

from wagtail import hooks
from wagtail.admin.menu import MenuItem

from versions import views


@hooks.register('register_admin_urls')
def register_versions_admin_url():
    return [path('versions/', views.versions, name='versions')]

@hooks.register('register_admin_menu_item')
def register_versions_menu_item():
  return MenuItem('Versions', reverse('versions'), icon_name='view', order=10000)
