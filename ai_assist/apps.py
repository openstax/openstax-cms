from django.apps import AppConfig


class AiAssistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_assist"

    def ready(self):
        from .panel_patches import apply_ai_panels
        from .vector_index import register_page_index

        apply_ai_panels()
        register_page_index()
