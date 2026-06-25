import datetime

from django.test import TestCase
from wagtail.models import Page, Site

from books.models import Book
from pages.custom_blocks import ContentCardBlock, ContentChooserBlock


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


class ContentCardBlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.objects.get(id=1)
        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": root, "is_default_site": True},
        )
        site.root_page = root
        site.save()
        Site.clear_site_root_paths_cache()
        cls.book = Book(
            title="Card Book", slug="card-book",
            salesforce_abbreviation="cb", salesforce_name="Card Book",
            publish_date=datetime.date.today(), locale=root.locale,
        )
        root.add_child(instance=cls.book)

    def test_card_emits_reference_and_set_overrides(self):
        block = ContentCardBlock()
        value = block.to_python({"reference": self.book.id, "excerpt": "Custom blurb"})
        rep = block.get_api_representation(value)
        self.assertEqual(rep["reference"]["type"], "books.book")
        self.assertEqual(rep["reference"]["url"], "/details/books/card-book")
        self.assertEqual(rep["excerpt"], "Custom blurb")

    def test_unset_overrides_serialize_as_null(self):
        # The CMS does NOT auto-fill overrides from the page; that merge is
        # frontend-side via `override ?? hydrated`. Unset overrides must serialize
        # as null (not "" or {}), or the JS nullish-coalesce would wrongly treat
        # an empty override as a real value and blank the field.
        block = ContentCardBlock()
        value = block.to_python({"reference": self.book.id})
        rep = block.get_api_representation(value)
        self.assertIsNone(rep["title"])
        self.assertIsNone(rep["image"])
        self.assertIsNone(rep["excerpt"])


class ContentCardRegistrationTests(TestCase):
    def test_content_card_registered_in_base_blocks(self):
        from pages.models.constants import BASE_CONTENT_BLOCKS
        names = [name for name, _ in BASE_CONTENT_BLOCKS]
        self.assertIn("content_card", names)
