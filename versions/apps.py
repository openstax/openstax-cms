"""
App configuration for the versions app.
"""

from django.apps import AppConfig


class VersionsConfig(AppConfig):
    """
    App configuration for the versions app.
    """
    name = 'versions'
    verbose_name = 'Versions'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import versions.signals 