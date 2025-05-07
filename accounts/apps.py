"""
App configuration for the accounts app.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    App configuration for the accounts app.
    """
    name = 'accounts'
    verbose_name = 'Accounts'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        # Import signal handlers
        # import accounts.signals 