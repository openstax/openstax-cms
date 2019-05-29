from django.conf.urls import include, url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from wagtailimportexport import admin_urls
from wagtailimportexport.compat import hooks, MenuItem, wagtailadmin_widgets


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^import-export/', include(admin_urls, namespace='wagtailimportexport_admin')),
    ]


class ImportExportMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.is_superuser


@hooks.register('register_admin_menu_item')
def register_import_export_menu_item():
    return ImportExportMenuItem(
        _('Import / Export'), reverse('wagtailimportexport_admin:index'), classnames='icon icon-download', order=800
    )

@hooks.register('register_page_listing_more_buttons')
def page_listing_more_buttons(page, page_perms, is_parent=False):
    if page.__class__.__name__ == "Book":
        yield wagtailadmin_widgets.Button('Duplicate Book', reverse('wagtailimportexport_admin:duplicate', args=[page.id]), priority=1)

@hooks.register('before_copy_page')
def before_copy_page(request, page):
    # Use a custom create view for the AwesomePage model
    return reverse('wagtailimportexport_admin:duplicate', args=[page.id])