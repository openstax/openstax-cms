from django.urls import include, path
from django.urls import reverse

from wagtail.core import hooks
from wagtail.admin import widgets as wagtailadmin_widgets

from duplicatebooks import admin_urls


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('duplicate/', include(admin_urls, namespace='duplicatebooks_admin')),
    ]

@hooks.register('register_page_listing_more_buttons')
def page_listing_more_buttons(page, page_perms, is_parent=False, next_url=None):
    if page.__class__.__name__ == "Book":
        yield wagtailadmin_widgets.Button('Duplicate Book', reverse('duplicatebooks_admin:duplicate', args=[page.id]), priority=1)
