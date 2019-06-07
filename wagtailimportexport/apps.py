from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WagtailImportExportAppConfig(AppConfig):
    name = 'wagtailimportexport'
    label = 'wagtailimportexport'
    verbose_name = _("Wagtail import-export")
