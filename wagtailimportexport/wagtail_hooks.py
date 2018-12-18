from django.conf.urls import include, url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from wagtailimportexport import admin_urls
from wagtailimportexport.compat import hooks, MenuItem


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
