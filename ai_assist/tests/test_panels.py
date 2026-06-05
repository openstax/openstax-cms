from django.apps import apps
from django.test import TestCase

from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.models import Page

from wagtail_ai.panels import AIDescriptionFieldPanel, AITitleFieldPanel


class AIPanelPatchTests(TestCase):
    def _page_models(self):
        return [
            m
            for m in apps.get_models()
            if isinstance(m, type) and issubclass(m, Page) and m is not Page
        ]

    def test_rootpage_uses_ai_panels(self):
        from pages.models import RootPage

        self.assertTrue(
            any(isinstance(p, AITitleFieldPanel) for p in RootPage.content_panels)
        )
        self.assertTrue(
            any(isinstance(p, AIDescriptionFieldPanel) for p in RootPage.promote_panels)
        )

    def test_no_page_keeps_a_plain_title_or_description_panel(self):
        for model in self._page_models():
            for panel in model.__dict__.get("content_panels", []):
                if getattr(panel, "field_name", None) == "title":
                    self.assertNotEqual(
                        type(panel), TitleFieldPanel, f"{model.__name__} title not swapped"
                    )
            for panel in model.__dict__.get("promote_panels", []):
                if getattr(panel, "field_name", None) == "search_description":
                    self.assertNotEqual(
                        type(panel), FieldPanel, f"{model.__name__} description not swapped"
                    )
