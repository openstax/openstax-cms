from django.conf.urls import url
from django.urls import reverse

from wagtail.core import hooks
from wagtail.admin.menu import MenuItem

from status import views


@hooks.register('register_admin_urls')
def register_status_admin_url():
    return [
        url(r'^status/', views.status, name='status'),
    ]

@hooks.register('register_admin_menu_item')
def register_status_menu_item():
  return MenuItem('Status', reverse('status'), icon_name='view', order=10000)
