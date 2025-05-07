"""
App configuration for the salesforce app.
"""

from django.apps import AppConfig


class SalesforceConfig(AppConfig):
    """
    App configuration for the salesforce app.
    """
    name = 'salesforce'
    verbose_name = 'Salesforce'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        Import signal handlers here to avoid circular imports.
        """
        pass
