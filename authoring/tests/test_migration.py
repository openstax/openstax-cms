# authoring/tests/test_migration.py
from django.test import TestCase
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock

from pages import models as page_models
from authoring.migration import sanitize_block, sanitize_raw_stream, build_export_payload


class SanitizeLeafTests(TestCase):
    def test_image_chooser_blanked_to_none(self):
        self.assertIsNone(sanitize_block(ImageChooserBlock(required=False), 88))

    def test_page_link_unwrapped_in_richtext(self):
        block = blocks.RichTextBlock()
        html = 'see <a linktype="page" id="12">the docs</a> now'
        self.assertEqual(sanitize_block(block, html), 'see the docs now')

    def test_image_embed_removed_in_richtext(self):
        block = blocks.RichTextBlock()
        html = 'before<embed embedtype="image" id="45" format="left"/>after'
        self.assertEqual(sanitize_block(block, html), 'beforeafter')

    def test_plain_charblock_untouched(self):
        block = blocks.CharBlock()
        self.assertEqual(sanitize_block(block, "Welcome"), "Welcome")


class SanitizeNestedTests(TestCase):
    def test_struct_with_nested_image_and_text(self):
        block = blocks.StructBlock([
            ("heading", blocks.CharBlock()),
            ("image", ImageChooserBlock(required=False)),
        ])
        raw = {"heading": "Hi", "image": 88}
        self.assertEqual(sanitize_block(block, raw), {"heading": "Hi", "image": None})

    def test_list_of_structs_recurses(self):
        block = blocks.ListBlock(blocks.StructBlock([
            ("book", SnippetChooserBlock("snippets.Subject")),
            ("label", blocks.CharBlock()),
        ]))
        raw = [{"type": "item", "id": "x", "value": {"book": 7, "label": "Bio"}}]
        result = sanitize_block(block, raw)
        self.assertEqual(result[0]["value"], {"book": None, "label": "Bio"})

    def test_struct_passes_through_unknown_keys(self):
        block = blocks.StructBlock([
            ("image", ImageChooserBlock(required=False)),
        ])
        raw = {"image": 88, "legacy_field": "stale"}
        result = sanitize_block(block, raw)
        self.assertIsNone(result["image"])           # known ref blanked
        self.assertEqual(result["legacy_field"], "stale")  # unknown key kept

    def test_stream_blanks_top_level_image_block(self):
        stream = blocks.StreamBlock([
            ("image", ImageChooserBlock(required=False)),
            ("para", blocks.CharBlock()),
        ])
        raw = [
            {"type": "image", "id": "a", "value": 88},
            {"type": "para", "id": "b", "value": "kept"},
        ]
        result = sanitize_raw_stream(stream, raw)
        self.assertIsNone(result[0]["value"])
        self.assertEqual(result[1]["value"], "kept")


# Note: `paragraph` is not a real block key in FlexPage.body — actual top-level
# block keys are: columns, divider, hero, html, section, tabbed_content.
# `html` (RawHTMLBlock) is the top-level raw-HTML block used here because it holds
# HTML content that may contain page-link tags. RawHTMLBlock is handled by
# _strip_richtext_refs, identical to RichTextBlock, so sanitization logic is identical.
DEFAULT_LAYOUT = [{"type": "default", "value": {}}]


class ExportPayloadTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)
        self.page = page_models.FlexPage(
            title="Sample", slug="sample",
            layout=DEFAULT_LAYOUT,
            body=[{"type": "html", "value": '<p>see <a linktype="page" id="999">x</a></p>'}],
        )
        self.home.add_child(instance=self.page)

    def test_payload_shape_and_sanitization(self):
        payload = build_export_payload(page_models.FlexPage.objects.get(id=self.page.id))
        self.assertEqual(set(payload), {"title", "slug", "layout", "body"})
        self.assertEqual(payload["title"], "Sample")
        self.assertEqual(payload["slug"], "sample")
        # the page link is unwrapped to its inner text
        self.assertIn("see x", payload["body"][0]["value"])
        self.assertNotIn("linktype", payload["body"][0]["value"])
