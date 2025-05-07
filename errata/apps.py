"""
App configuration for the errata app.
"""

from django.apps import AppConfig


class ErrataConfig(AppConfig):
    """
    App configuration for the errata app.
    """
    name = 'errata'
    verbose_name = 'Errata'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
