"""
App configuration for the books app.
"""

from django.apps import AppConfig


class BooksConfig(AppConfig):
    """
    App configuration for the books app.
    """
    name = 'books'
    verbose_name = 'Books'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import books.signals 