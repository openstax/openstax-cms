import datetime

from django.apps import apps
from django.test import TestCase
from wagtail.models import Page, Site
from wagtail.fields import RichTextField
from wagtail.api import APIField
from books.models import Book
from openstax.api_fields import ExpandedRichTextField


class ExpandedRichTextFieldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Ensure a Site exists so page.url resolves to a frontend route.
        root = Page.objects.get(id=1)
        # Point (or create) the default site at root so the book page is
        # within the site tree and get_url_parts can resolve a URL.
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            site = Site.objects.create(
                hostname="localhost", root_page=root, is_default_site=True
            )
        else:
            site.root_page = root
            site.save()
        cls.site = site
        # Clear the site root paths cache so the updated site is used.
        Site.clear_site_root_paths_cache()

        cls.book = Book(
            title="Test Book", slug="test-book",
            salesforce_abbreviation="tb", salesforce_name="Test Book",
            publish_date=datetime.date.today(),
            locale=root.locale,
        )
        root.add_child(instance=cls.book)

    def test_expands_internal_page_link_to_frontend_route(self):
        field = ExpandedRichTextField()
        html = f'<a linktype="page" id="{self.book.id}">go</a>'
        out = field.to_representation(html)
        # Book.get_url_parts maps the tree page onto /details/books/<slug>
        self.assertIn('href="/details/books/test-book"', out)
        self.assertNotIn('linktype="page"', out)

    def test_missing_page_yields_bare_anchor(self):
        field = ExpandedRichTextField()
        out = field.to_representation('<a linktype="page" id="999999">x</a>')
        self.assertIn("<a>", out)

    def test_none_and_empty_are_safe(self):
        field = ExpandedRichTextField()
        self.assertEqual(field.to_representation(None), "")
        self.assertEqual(field.to_representation(""), "")


from wagtail import blocks as wagtail_blocks
from wagtail.fields import StreamField
from pages.custom_blocks import APIRichTextBlock


def _leaf_blocks(block):
    """Recursively yield every leaf block in a block tree."""
    child_blocks = getattr(block, "child_blocks", None)
    single_child = getattr(block, "child_block", None)
    if child_blocks:
        for child in child_blocks.values():
            yield from _leaf_blocks(child)
    elif single_child is not None:
        yield from _leaf_blocks(single_child)
    else:
        yield block


class StreamFieldRichTextTests(TestCase):
    def test_no_streamfield_uses_plain_richtextblock(self):
        offenders = []
        for model in apps.get_models():
            for f in model._meta.get_fields():
                if not isinstance(f, StreamField):
                    continue
                for leaf in _leaf_blocks(f.stream_block):
                    # APIRichTextBlock (subclass) is allowed; plain is not.
                    if type(leaf) is wagtail_blocks.RichTextBlock:
                        offenders.append(f"{model._meta.label}.{f.name}")
        self.assertEqual(sorted(set(offenders)), [], f"Plain RichTextBlock in: {set(offenders)}")


class ModelRichTextWiringTests(TestCase):
    def test_every_api_exposed_richtextfield_uses_expanded_serializer(self):
        offenders = []
        for model in apps.get_models():
            rtf_names = {
                f.name for f in model._meta.get_fields()
                if isinstance(f, RichTextField)
            }
            for entry in getattr(model, "api_fields", []) or []:
                name = entry.name if isinstance(entry, APIField) else entry
                if name not in rtf_names:
                    continue
                ok = (
                    isinstance(entry, APIField)
                    and isinstance(entry.serializer, ExpandedRichTextField)
                )
                if not ok:
                    offenders.append(f"{model._meta.app_label}.{model.__name__}.{name}")
        self.assertEqual(offenders, [], f"Unwired RichTextFields: {offenders}")


from pages.custom_blocks import LinkBlock


class LinkBlockTargetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.objects.get(id=1)
        site, _ = Site.objects.get_or_create(
            hostname="localhost", defaults={"root_page": root, "is_default_site": True}
        )
        # Make sure the default site points at the tree root so page.url resolves.
        site.root_page = root
        site.save()
        Site.clear_site_root_paths_cache()
        cls.book = Book(
            title="LB Book", slug="lb-book",
            salesforce_abbreviation="lb", salesforce_name="LB Book",
            publish_date=datetime.date.today(), locale=root.locale,
        )
        root.add_child(instance=cls.book)

    def test_internal_link_returns_frontend_url_not_tree_path(self):
        block = LinkBlock()
        value = block.to_python([{"type": "internal", "value": self.book.id}])
        rep = block.get_api_representation(value)
        self.assertEqual(rep["type"], "internal")
        # page.url honors Book.get_url_parts → /details/books/<slug> (no trailing slash)
        self.assertEqual(rep["value"], "/details/books/lb-book")
