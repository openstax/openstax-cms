import datetime

from django.test import TestCase
from wagtail.models import Page, Site

from books.models import Book
from pages.custom_blocks import ContentChooserBlock


class ContentChooserBlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.objects.get(id=1)
        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": root, "is_default_site": True},
        )
        # Ensure the default site points at the tree root so page.url resolves.
        site.root_page = root
        site.save()
        Site.clear_site_root_paths_cache()
        cls.book = Book(
            title="CR Book", slug="cr-book",
            salesforce_abbreviation="cr", salesforce_name="CR Book",
            publish_date=datetime.date.today(), locale=root.locale,
        )
        root.add_child(instance=cls.book)

    def test_reference_returns_canonical_shape(self):
        block = ContentChooserBlock()
        value = block.to_python(self.book.id)  # PageChooserBlock.to_python(pk) -> Page
        rep = block.get_api_representation(value)
        self.assertEqual(rep["id"], self.book.id)
        self.assertEqual(rep["type"], "books.book")
        self.assertEqual(rep["slug"], "cr-book")
        # Book.get_url_parts maps the tree page onto /details/books/<slug> (via .specific)
        self.assertEqual(rep["url"], "/details/books/cr-book")
        self.assertEqual(rep["title"], "CR Book")

    def test_empty_reference_returns_none(self):
        block = ContentChooserBlock()
        self.assertIsNone(block.get_api_representation(None))

    def test_allowlist_restricts_page_types(self):
        block = ContentChooserBlock()
        # page_type defaults to CONTENT_REFERENCE_TYPES; Book is resolvable.
        self.assertIn(Book, block.target_models)
