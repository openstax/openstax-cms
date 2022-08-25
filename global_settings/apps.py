from django.apps import AppConfig

class GlobalSettingsConfig(AppConfig):
    name = 'global_settings'
    verbose_name = 'global_settings'

    def ready(self):
        import global_settings.signals  # noqa
        import api.signals
        import donations.signals
        import webinars.signals
        import snippets.signals
