from django.apps import AppConfig


class GlobalSettingsConfig(AppConfig):
    name = 'global_settings'
    verbose_name = 'global_settings'
    default = True

    def ready(self):
        import global_settings.signals  # noqa
        import api.signals
        import donations.signals
        import webinars.signals
        import snippets.signals
        import salesforce.signals
        import oxmenus.signals

        # Register cross-cutting system checks (keeps settings/base.py declarative).
        import global_settings.checks  # noqa: F401

        # Apply the wagtail-transfer Objective base-model patch in every process
        # that runs django.setup(), not just when the URLconf is imported.
        from openstax.wagtail_transfer_patches import apply_patches
        apply_patches()
