"""
App configuration for the api app.
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    App configuration for the api app.
    """
    name = 'api'
    verbose_name = 'API'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        pass
