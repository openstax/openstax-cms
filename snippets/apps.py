"""
App configuration for the snippets app.
"""

from django.apps import AppConfig


class SnippetsConfig(AppConfig):
    """
    App configuration for the snippets app.
    """
    name = 'snippets'
    verbose_name = 'Snippets'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        pass
