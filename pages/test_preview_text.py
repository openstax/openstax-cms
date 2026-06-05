from django.test import TestCase

from wagtail import blocks

from pages.preview_text import extract_page_text, stream_searchable_text


def _stream_value():
    block = blocks.StreamBlock(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("heading", blocks.CharBlock()),
        ]
    )
    return block.to_python(
        [
            {"type": "paragraph", "value": "<p>OpenStax is a nonprofit initiative.</p>"},
            {"type": "heading", "value": "Free for all"},
        ]
    )


class StreamSearchableTextTests(TestCase):
    def test_extracts_text_and_strips_html(self):
        text = stream_searchable_text(_stream_value())
        self.assertIn("OpenStax is a nonprofit initiative", text)
        self.assertIn("Free for all", text)
        self.assertNotIn("<p>", text)

    def test_none_is_safe(self):
        self.assertEqual(stream_searchable_text(None), "")


class ExtractPageTextTests(TestCase):
    def test_walks_a_real_page_instance_without_error(self):
        # A real page model has FKs, reverse relations, StreamFields, etc.
        # extract_page_text must walk them defensively and pull text fields
        # (here, the title) without raising on the non-text ones.
        from pages.models import RootPage

        page = RootPage(title="Home Page Title")
        text = extract_page_text(page)
        self.assertIn("Home Page Title", text)
