"""
App configuration for the redirects app.
"""

from django.apps import AppConfig


class RedirectsConfig(AppConfig):
    """
    App configuration for the redirects app.
    """
    name = 'redirects'
    verbose_name = 'Redirects'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import redirects.signals 