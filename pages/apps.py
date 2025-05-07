"""
App configuration for the pages app.
"""

from django.apps import AppConfig


class PagesConfig(AppConfig):
    """
    App configuration for the pages app.
    """
    name = 'pages'
    verbose_name = 'Pages'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import redirects.signals 