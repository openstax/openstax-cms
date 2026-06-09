import datetime

from django.test import TestCase
from wagtail.models import Page, Site
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
