from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class GlobalSettingsConfig(AppConfig):
    name = 'global_settings'
    verbose_name = _('global_settings')

    def ready(self):
        import global_settings.signals  # noqa
