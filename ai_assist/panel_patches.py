from django.apps import apps as django_apps


def _swap(model, attr, match_cls, field_name, new_cls):
    panels = model.__dict__.get(attr)
    if not panels:
        return
    for i, panel in enumerate(panels):
        if type(panel) is match_cls and getattr(panel, "field_name", None) == field_name:
            panels[i] = new_cls(**panel.clone_kwargs())


def apply_ai_panels():
    """Swap the title and search_description panels of every page type for the
    wagtail-ai equivalents, so the AI suggestion button appears on all pages."""
    from wagtail.admin.panels import FieldPanel, TitleFieldPanel
    from wagtail.models import Page

    from wagtail_ai.panels import AIDescriptionFieldPanel, AITitleFieldPanel

    for model in django_apps.get_models():
        if not (isinstance(model, type) and issubclass(model, Page)):
            continue
        _swap(model, "content_panels", TitleFieldPanel, "title", AITitleFieldPanel)
        _swap(model, "promote_panels", FieldPanel, "search_description", AIDescriptionFieldPanel)
