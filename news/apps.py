"""
App configuration for the news app.
"""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """
    App configuration for the news app.
    """
    name = 'news'
    verbose_name = 'News'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import news.signals 