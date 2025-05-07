"""
App configuration for the mail app.
"""

from django.apps import AppConfig


class MailConfig(AppConfig):
    """
    App configuration for the mail app.
    """
    name = 'mail'
    verbose_name = 'Mail'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers if they exist
        # import mail.signals 