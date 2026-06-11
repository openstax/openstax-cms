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
        # NOTE: This test introspects Django model fields via _meta.get_fields().
        # It cannot detect Python *property*-based proxy fields (e.g.
        # books.FacultyResources.resource_description and
        # books.StudentResources.resource_description) because those are not
        # Django fields and are invisible to _meta.  Those known cases are
        # explicitly asserted in test_known_proxy_property_richtext_fields_are_wired
        # below and must be wired manually whenever new proxy properties are added.
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

    def test_known_proxy_property_richtext_fields_are_wired(self):
        # Properties proxying to a RichTextField are invisible to _meta.get_fields(),
        # so the structural guard above can't see them — assert the known ones explicitly.
        from books.models import FacultyResources, StudentResources
        for model in (FacultyResources, StudentResources):
            entry = next(
                e for e in model.api_fields
                if isinstance(e, APIField) and e.name == 'resource_description'
            )
            self.assertIsInstance(entry.serializer, ExpandedRichTextField)


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

    def test_internal_link_with_no_page_returns_none(self):
        # PageChooserBlock(required=False) allows an internal sub-block with no
        # page chosen; child.value is None in that case.  Confirm get_api_representation
        # returns None instead of raising AttributeError on child.value.specific.
        block = LinkBlock()
        # to_python with value=None produces a StreamValue child where child.value is None.
        value = block.to_python([{"type": "internal", "value": None}])
        self.assertIsNone(block.get_api_representation(value))
