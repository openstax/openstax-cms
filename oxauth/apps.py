"""
App configuration for the oxauth app.
"""

from django.apps import AppConfig


class OxauthConfig(AppConfig):
    """
    App configuration for the oxauth app.
    """
    name = 'oxauth'
    verbose_name = 'OpenStax Auth'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import oxauth.signals 