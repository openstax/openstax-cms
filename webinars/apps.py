"""
App configuration for the webinars app.
"""

from django.apps import AppConfig


class WebinarsConfig(AppConfig):
    """
    App configuration for the webinars app.
    """
    name = 'webinars'
    verbose_name = 'Webinars'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        pass
