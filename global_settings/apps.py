"""
App configuration for the global_settings app.
"""

from django.apps import AppConfig


class GlobalSettingsConfig(AppConfig):
    """
    App configuration for the global_settings app.
    """
    name = 'global_settings'
    verbose_name = 'Global Settings'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        import global_settings.signals  # noqa
        import api.signals
        import donations.signals
        import webinars.signals
        import snippets.signals
        import salesforce.signals
        import oxmenus.signals
