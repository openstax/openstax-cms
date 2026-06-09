from django.apps import apps
from django.test import SimpleTestCase

from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.models import Page

from wagtail_ai.panels import AIDescriptionFieldPanel, AITitleFieldPanel


def _walk(panel):
    """Yield every panel in a (model-bound) panel definition tree."""
    yield panel
    for child in getattr(panel, "children", []) or []:
        yield from _walk(child)


def _panels_of(model):
    """All panels in the model's fully built + bound edit handler.

    Using the bound handler (not the raw class attributes) is what makes this a
    real test: it expands PanelPlaceholders and walks custom ``edit_handler``
    trees exactly as the Wagtail admin does, so it sees what an editor sees.
    """
    return list(_walk(model.get_edit_handler()))


class AIPanelPatchTests(SimpleTestCase):
    def _page_models(self):
        return [
            m
            for m in apps.get_models()
            if isinstance(m, type) and issubclass(m, Page) and m is not Page
        ]

    def test_rootpage_uses_ai_panels(self):
        # RootPage declares concrete content/promote panels (the path the
        # original implementation already handled).
        from pages.models import RootPage

        panels = _panels_of(RootPage)
        self.assertTrue(any(isinstance(p, AITitleFieldPanel) for p in panels))
        self.assertTrue(any(isinstance(p, AIDescriptionFieldPanel) for p in panels))

    def test_edit_handler_model_uses_ai_panels(self):
        # books.Book drives its admin through a custom edit_handler with the
        # title/description buried in nested ObjectLists + PanelPlaceholders.
        # This is the case the previous implementation silently skipped.
        from books.models import Book

        panels = _panels_of(Book)
        self.assertTrue(
            any(isinstance(p, AITitleFieldPanel) for p in panels),
            "Book's title panel was not swapped for AITitleFieldPanel",
        )
        self.assertTrue(
            any(isinstance(p, AIDescriptionFieldPanel) for p in panels),
            "Book's search_description panel was not swapped for AIDescriptionFieldPanel",
        )

    def test_no_page_keeps_a_plain_title_or_description_panel(self):
        # Across every page type, no editor should still show a plain
        # (non-AI) title or search_description field.
        for model in self._page_models():
            panels = _panels_of(model)
            for panel in panels:
                field_name = getattr(panel, "field_name", None)
                if field_name == "title":
                    self.assertNotEqual(
                        type(panel),
                        TitleFieldPanel,
                        f"{model.__name__} has an un-swapped plain title panel",
                    )
                if field_name == "search_description":
                    self.assertNotEqual(
                        type(panel),
                        FieldPanel,
                        f"{model.__name__} has an un-swapped plain search_description panel",
                    )
