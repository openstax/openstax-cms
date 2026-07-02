from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page, Site

import snippets.models
from pages.models import RootPage
from books.models import (
    BookIndex,
    Book,
    BookCategories,
    BookFacultyResources,
    BookStudentResources,
    BookSubjects,
    K12BookSubjects,
)
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from salesforce.tests import openstax_vcr as vcr
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from unittest.mock import patch
from wagtail.documents.models import Document
import datetime


class BookTests(WagtailPageTestCase):

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        # create root page
        root_page = Page.objects.get(title="Root")
        # create homepage
        homepage = RootPage(title="Hello World",
                            slug="hello-world",
                            )
        # add homepage to root page
        root_page.add_child(instance=homepage)
        # create book index page
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test",
                               )
        # add book index to homepage
        homepage.add_child(instance=book_index)

        # Point the default site at our homepage so the Wagtail Pages API works
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()

        test_image = SimpleUploadedFile(name='openstax.png', content=open("pages/static/images/openstax.png", 'rb').read())
        cls.test_doc = Document.objects.create(title='Test Doc', file=test_image)

        cls.book_index = Page.objects.get(id=book_index.id)

    def test_can_create_book(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'University Physics (Calc)')

    def test_book_urls_collects_link_fields(self):
        # Regression: api_fields holds APIField instances, not strings, so the
        # old getattr(self, field) raised TypeError on every iteration and
        # book_urls() silently returned [] for every book. See PR #1684.
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        webview_link="https://openstax.org/books/university-physics",
                        amazon_link="https://amazon.com/dp/university-physics",
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            found = [url for group in book.book_urls() for url in group]
            self.assertTrue(found, "book_urls() should not be empty when link fields are set")
            # The pre-existing regex captures the host (it stops at the first
            # path '/'), so assert on the host portion of each link field.
            self.assertIn("https://openstax.org", found)
            self.assertIn("https://amazon.com", found)

    def test_can_create_ap_book(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_prealgebra.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Prealgebra",
                        slug="prealgebra",
                        salesforce_book_id='a0ZU000000DLpEMMA1',
                        description="This is Prealgebra. Next, you learn Prealgebra!",
                        is_ap=True,
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')


    def test_book_callout_snippet_exists_and_is_editable(self):
        from wagtail.models import Locale
        from books.models import BookCallout
        callout = BookCallout.objects.create(
            locale=Locale.get_default(),
            rex_callout_title='Recommended',
            rex_callout_blurb='Highlight and add notes — 100% free!',
        )
        self.assertEqual(BookCallout.objects.count(), 1)
        self.assertEqual(callout.rex_callout_title, 'Recommended')
        # webinar_content is a StreamField (empty is fine)
        self.assertEqual(list(callout.webinar_content), [])

    def test_callout_fields_sourced_from_snippet(self):
        from books.models import BookCallout
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            BookCallout.objects.create(
                locale=root_page.locale,
                rex_callout_title='Shared Title',
                rex_callout_blurb='Shared Blurb',
            )
            book = Book(title="Callout Book", slug="callout-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test", cover=self.test_doc, title_image=self.test_doc,
                        publish_date=datetime.date.today(), locale=root_page.locale)
            book_index.add_child(instance=book)
            # property reads the snippet
            self.assertEqual(book.rex_callout_title, 'Shared Title')
            self.assertEqual(book.rex_callout_blurb, 'Shared Blurb')
            # API still exposes the same keys with the same types
            resp = self.client.get(
                '/apps/cms/api/v2/pages/{}/?fields=rex_callout_title,rex_callout_blurb,webinar_content'.format(book.id))
            data = resp.json()
            self.assertEqual(data['rex_callout_title'], 'Shared Title')
            self.assertEqual(data['rex_callout_blurb'], 'Shared Blurb')
            self.assertEqual(data['webinar_content'], [])   # empty StreamField -> []

    def test_cover_is_image_with_alt_and_url_fallback(self):
        from wagtail.images import get_image_model
        from django.core.files.uploadedfile import SimpleUploadedFile
        Image = get_image_model()
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            with open('pages/static/images/openstax.png', 'rb') as f:
                image_bytes = f.read()
            img = Image.objects.create(
                title='Cover img',
                description='A maths textbook cover',
                file=SimpleUploadedFile('c.png', image_bytes),
            )
            book = Book(title="Img Book", slug="img-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test",
                        cover_image=img, banner_image=img,
                        publish_date=datetime.date.today(), locale=root_page.locale)
            book_index.add_child(instance=book)
            resp = self.client.get(
                '/apps/cms/api/v2/pages/{}/?fields=cover_url,title_image_url,cover_alt,title_image_alt'.format(book.id))
            data = resp.json()
            self.assertTrue(data['cover_url'])                      # non-empty URL string
            self.assertTrue(data['title_image_url'])                # non-empty URL string
            self.assertEqual(data['cover_alt'], 'A maths textbook cover')
            self.assertEqual(data['title_image_alt'], 'A maths textbook cover')

    def test_cover_url_falls_back_to_legacy_document(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Legacy Book", slug="legacy-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test",
                        cover=self.test_doc, title_image=self.test_doc,
                        publish_date=datetime.date.today(), locale=root_page.locale)
            book_index.add_child(instance=book)
            # No Image set yet -> url falls back to the legacy document
            self.assertTrue(book.cover_url)
            self.assertTrue(book.title_image_url)
            self.assertIsNone(book.cover_alt)   # no Image -> no alt
            self.assertIsNone(book.title_image_alt)   # no Image -> no alt

    def test_convert_book_images_command(self):
        from django.core.management import call_command
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Convert Book", slug="convert-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test",
                        cover=self.test_doc, title_image=self.test_doc,
                        publish_date=datetime.date.today(), locale=root_page.locale)
            book_index.add_child(instance=book)
            self.assertIsNone(book.cover_image)

            call_command('convert_book_images')

            book.refresh_from_db()
            self.assertIsNotNone(book.cover_image)        # Image created + linked
            self.assertIsNotNone(book.banner_image)
            self.assertTrue(book.cover_url)
            # Idempotent: a second run does not create duplicates / change links
            first_cover_id = book.cover_image_id
            call_command('convert_book_images')
            book.refresh_from_db()
            self.assertEqual(book.cover_image_id, first_cover_id)

    def test_convert_book_images_continues_after_bad_document(self):
        from django.core.management import call_command
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            broken_doc = Document.objects.create(
                title='Broken Doc',
                file=SimpleUploadedFile('broken.png', b'not a real image'))
            bad_book = Book(title="Bad Book", slug="bad-book",
                        book_uuid='11111111-1111-1111-1111-111111111111',
                        description="Test", cover=broken_doc,
                        publish_date=datetime.date.today(), locale=root_page.locale)
            book_index.add_child(instance=bad_book)
            good_book = Book(title="Good Book", slug="good-book",
                        book_uuid='22222222-2222-2222-2222-222222222222',
                        description="Test", cover=self.test_doc,
                        publish_date=datetime.date.today(), locale=root_page.locale)
            book_index.add_child(instance=good_book)

            call_command('convert_book_images')  # must not raise/abort

            bad_book.refresh_from_db()
            good_book.refresh_from_db()
            self.assertIsNone(bad_book.cover_image)          # skipped, not converted
            self.assertIsNotNone(good_book.cover_image)      # still converted despite the earlier failure

    def test_salesforce_name_is_synced_dropdown(self):
        from django import forms as dj_forms
        from books.models import Book
        from salesforce.models import SalesforceBookName
        SalesforceBookName.objects.create(
            salesforce_id='a1', name='UP', official_name='University Physics (Calculus)')
        SalesforceBookName.objects.create(
            salesforce_id='a2', name='CA', official_name='College Algebra')

        form_class = Book.get_edit_handler().get_form_class()

        form = form_class(instance=Book(salesforce_name=''))
        field = form.fields['salesforce_name']
        self.assertIsInstance(field, dj_forms.ChoiceField)
        values = [c[0] for c in field.choices]
        self.assertIn('University Physics (Calculus)', values)
        self.assertIn('College Algebra', values)

        # An existing value not in the synced list is preserved as an option
        form2 = form_class(instance=Book(salesforce_name='Legacy Drifted Name'))
        values2 = [c[0] for c in form2.fields['salesforce_name'].choices]
        self.assertIn('Legacy Drifted Name', values2)

    def test_book_uuid_is_canonical_and_syncs_cnx_id(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="UUID Sync Book",
                        slug="uuid-sync-book",
                        book_uuid='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale)
            book_index.add_child(instance=book)
            book.refresh_from_db()
            # cnx_id mirrors the canonical book_uuid
            self.assertEqual(book.cnx_id, 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
            # cnx_id stays a real, filterable column
            self.assertTrue(
                Book.objects.filter(cnx_id='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee').exists()
            )

    def test_legacy_cnx_id_backfills_book_uuid(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Legacy CNX Book",
                        slug="legacy-cnx-book",
                        cnx_id='bbbbbbbb-cccc-dddd-eeee-ffffffffffff',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale)
            book_index.add_child(instance=book)
            book.refresh_from_db()
            self.assertEqual(book.book_uuid, 'bbbbbbbb-cccc-dddd-eeee-ffffffffffff')
            self.assertEqual(book.cnx_id, 'bbbbbbbb-cccc-dddd-eeee-ffffffffffff')
            self.assertTrue(
                Book.objects.filter(cnx_id='bbbbbbbb-cccc-dddd-eeee-ffffffffffff').exists()
            )

    def test_pdf_api_keys(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="PDF Book", slug="pdf-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test", cover=self.test_doc, title_image=self.test_doc,
                        pdf=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale)
            book_index.add_child(instance=book)
            resp = self.client.get(
                '/apps/cms/api/v2/pages/{}/?fields=pdf_url,high_resolution_pdf_url'.format(book.id))
            data = resp.json()
            self.assertIn('pdf_url', data)
            self.assertIn('high_resolution_pdf_url', data)            # deprecated alias retained
            self.assertEqual(data['pdf_url'], data['high_resolution_pdf_url'])
            self.assertNotIn('low_resolution_pdf_url', data)

    def test_dead_fields_removed_from_api(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Lean Book", slug="lean-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test", cover=self.test_doc, title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale)
            book_index.add_child(instance=book)
            resp = self.client.get('/apps/cms/api/v2/pages/{}/?fields=*'.format(book.id))
            data = resp.json()
            for gone in ['ibook_link', 'ibook_link_volume_2', 'ibook_isbn_13',
                         'ibook_volume_2_isbn_13', 'enable_study_edge', 'tutor_marketing_book',
                         'amazon_iframe', 'comp_copy_available', 'comp_copy_content']:
                self.assertNotIn(gone, data)

    def test_kindle_chegg_removed_from_api(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="No KC Book", slug="no-kc-book",
                        book_uuid='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test", cover=self.test_doc, title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale)
            book_index.add_child(instance=book)
            resp = self.client.get('/apps/cms/api/v2/pages/{}/?fields=*'.format(book.id))
            data = resp.json()
            for gone in ['kindle_link', 'chegg_link', 'chegg_link_text']:
                self.assertNotIn(gone, data)

    def test_can_create_book_without_cnx_id(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_no_cnx_id.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="This is University Physics. Next, you learn University Physics!",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'University Physics (Calc)')

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(BookIndex, {
            Book
        })

    def test_cannot_create_book_under_homepage(self):
        self.assertCanNotCreateAt(RootPage, Book)

    def test_slashless_apis_are_good(self):
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/books')
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/books/slug')

    def test_can_create_book_with_cc_license(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_license.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale,
                        license_name='Creative Commons Attribution License',
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.license_url, 'https://creativecommons.org/licenses/by/4.0/')

    def test_faculty_resources_available_or_not(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)

        faculty_resource = snippets.models.FacultyResource(heading="Instructor Getting Started Guide",
                                                           description="<p data-block-key=\"6o2yl\">Download our helpful guide to all things OpenStax.<br/></p>",
                                                           unlocked_resource=False,
                                                           creator_fest_resource=False)
        faculty_resource.save()

        book_faculty_resource = BookFacultyResources.objects.create(link_external="https://openstax.org",
                                                                    link_text="Go!", resource=faculty_resource,
                                                                    book_faculty_resource=book)
        book_faculty_resource.save()

        # run test without flag
        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics')
        self.assertEqual(response.data['book_faculty_resources'][0]['link_external'], 'https://openstax.org')
        # check book data is cleared out
        self.assertEqual(response.data['book_faculty_resources'][0]['book_faculty_resource'], {})

        # run test with flag
        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics&x=y')
        self.assertEqual(response.data['book_faculty_resources'][0]['link_external'], '')

    def test_bad_faculty_resources_slug(self):
        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physic')
        self.assertEqual(response.data, {})

    def test_retired_resources_not_found(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/retired_book.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="College Physics",
                        slug="college-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale,
                        license_name='Creative Commons Attribution License',
                        book_state='retired'
                        )
            book_index.add_child(instance=book)

            response = self.client.get('/apps/cms/api/books/resources/?slug=college-physics')
            self.assertIn(b'This book is retired', response.content)

    def test_hidden_faculty_resources_filtered_from_resources_api(self):
        """Hidden faculty resources should not appear in the resources API response."""
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics-hidden",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)

        faculty_resource = snippets.models.FacultyResource(heading="Visible Resource",
                                                           description="Visible",
                                                           unlocked_resource=False,
                                                           creator_fest_resource=False)
        faculty_resource.save()

        hidden_faculty_resource = snippets.models.FacultyResource(heading="Hidden Resource",
                                                                   description="Hidden",
                                                                   unlocked_resource=False,
                                                                   creator_fest_resource=False)
        hidden_faculty_resource.save()

        BookFacultyResources.objects.create(link_external="https://openstax.org",
                                            link_text="Visible", resource=faculty_resource,
                                            book_faculty_resource=book)
        BookFacultyResources.objects.create(link_external="https://openstax.org/hidden",
                                            link_text="Hidden", resource=hidden_faculty_resource,
                                            book_faculty_resource=book, hidden=True)

        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics-hidden')
        self.assertEqual(len(response.data['book_faculty_resources']), 1)
        self.assertEqual(response.data['book_faculty_resources'][0]['link_text'], 'Visible')

    def test_hidden_faculty_resources_filtered_from_pages_api(self):
        """HiddenFilterChildRelationField excludes hidden faculty resources from Wagtail Pages API."""
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics-hidden-pages",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)

        faculty_resource = snippets.models.FacultyResource(heading="Visible Resource",
                                                           description="Visible",
                                                           unlocked_resource=False,
                                                           creator_fest_resource=False)
        faculty_resource.save()

        hidden_faculty_resource = snippets.models.FacultyResource(heading="Hidden Resource",
                                                                   description="Hidden",
                                                                   unlocked_resource=False,
                                                                   creator_fest_resource=False)
        hidden_faculty_resource.save()

        BookFacultyResources.objects.create(link_external="https://openstax.org",
                                            link_text="Visible", resource=faculty_resource,
                                            book_faculty_resource=book)
        BookFacultyResources.objects.create(link_external="https://openstax.org/hidden",
                                            link_text="Hidden", resource=hidden_faculty_resource,
                                            book_faculty_resource=book, hidden=True)

        response = self.client.get('/apps/cms/api/v2/pages/{}/?fields=book_faculty_resources'.format(book.pk))
        faculty_resources = response.data['book_faculty_resources']
        self.assertEqual(len(faculty_resources), 1)
        self.assertEqual(faculty_resources[0]['link_text'], 'Visible')

    def test_hidden_student_resources_filtered_from_pages_api(self):
        """HiddenFilterChildRelationField excludes hidden student resources from Wagtail Pages API."""
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics-hidden-student",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)

        student_resource = snippets.models.StudentResource(heading="Visible Student Resource",
                                                            description="Visible",
                                                            unlocked_resource=True)
        student_resource.save()

        hidden_student_resource = snippets.models.StudentResource(heading="Hidden Student Resource",
                                                                    description="Hidden",
                                                                    unlocked_resource=True)
        hidden_student_resource.save()

        BookStudentResources.objects.create(link_external="https://openstax.org",
                                            link_text="Visible", resource=student_resource,
                                            book_student_resource=book)
        BookStudentResources.objects.create(link_external="https://openstax.org/hidden",
                                            link_text="Hidden", resource=hidden_student_resource,
                                            book_student_resource=book, hidden=True)

        response = self.client.get('/apps/cms/api/v2/pages/{}/?fields=book_student_resources'.format(book.pk))
        student_resources = response.data['book_student_resources']
        self.assertEqual(len(student_resources), 1)
        self.assertEqual(student_resources[0]['link_text'], 'Visible')

    @patch('books.models.capture_exception')
    def test_page_api_book_list_skips_missing_book_promote_snippet(self, capture_exception):
        book_index = BookIndex.objects.all()[0]
        root_page = Page.objects.get(title="Root")
        promote_snippet = snippets.models.PromoteSnippet.objects.create(name="Assignable")
        book = Book(
            title="Promoted Book",
            slug="promoted-book",
            description="Test Book",
            cover=self.test_doc,
            title_image=self.test_doc,
            publish_date=datetime.date.today(),
            locale=root_page.locale,
            promote_snippet=[
                {"type": "content", "value": promote_snippet.id},
                {"type": "content", "value": None},
            ],
        )
        book_index.add_child(instance=book)

        page = RootPage.objects.get(slug="hello-world")
        page.body = [
            {
                "type": "section",
                "value": {
                    "content": [
                        {
                            "type": "book_list",
                            "value": {"books": [book.id]},
                        }
                    ],
                    "config": [],
                },
            },
        ]
        page.save_revision().publish()

        response = self.client.get('/apps/cms/api/v2/pages/{}/?fields=body'.format(page.pk))

        self.assertEqual(response.status_code, 200)
        capture_exception.assert_not_called()
        book_data = response.data['body'][0]['value']['content'][0]['value']['books'][0]
        self.assertEqual(book_data['id'], book.id)
        self.assertEqual(book_data['promote_snippet'][0]['value']['name'], 'Assignable')
        self.assertEqual(book_data['promote_snippet'][1]['type'], 'content')
        self.assertIsNone(book_data['promote_snippet'][1]['value'])
        self.assertEqual(book_data['promote_tags'], ['Assignable'])

    @patch('books.models.capture_exception')
    def test_page_api_book_list_skips_missing_book_subject_relations(self, capture_exception):
        book_index = BookIndex.objects.all()[0]
        root_page = Page.objects.get(title="Root")
        book = Book(
            title="Book With Missing Subjects",
            slug="book-with-missing-subjects",
            description="Test Book",
            cover=self.test_doc,
            title_image=self.test_doc,
            publish_date=datetime.date.today(),
            locale=root_page.locale,
        )
        book_index.add_child(instance=book)
        BookSubjects.objects.create(book_subject=book, subject=None)
        K12BookSubjects.objects.create(k12book_subject=book, subject=None)
        BookCategories.objects.create(book_category=book, category=None)

        page = RootPage.objects.get(slug="hello-world")
        page.body = [
            {
                "type": "section",
                "value": {
                    "content": [
                        {
                            "type": "book_list",
                            "value": {"books": [book.id]},
                        }
                    ],
                    "config": [],
                },
            },
        ]
        page.save_revision().publish()

        response = self.client.get('/apps/cms/api/v2/pages/{}/?fields=body'.format(page.pk))

        self.assertEqual(response.status_code, 200)
        capture_exception.assert_not_called()
        book_data = response.data['body'][0]['value']['content'][0]['value']['books'][0]
        self.assertEqual(book_data['id'], book.id)
        self.assertEqual(book_data['subjects'], [])
        self.assertEqual(book_data['k12subject'], [])
        self.assertEqual(book_data['subject_categories'], [])

    def test_non_hidden_resources_still_appear(self):
        """Resources with hidden=False (default) should appear normally."""
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics-not-hidden",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)

        faculty_resource = snippets.models.FacultyResource(heading="Resource 1",
                                                           description="First",
                                                           unlocked_resource=False,
                                                           creator_fest_resource=False)
        faculty_resource.save()

        faculty_resource_2 = snippets.models.FacultyResource(heading="Resource 2",
                                                              description="Second",
                                                              unlocked_resource=False,
                                                              creator_fest_resource=False)
        faculty_resource_2.save()

        BookFacultyResources.objects.create(link_external="https://openstax.org/1",
                                            link_text="First", resource=faculty_resource,
                                            book_faculty_resource=book)
        BookFacultyResources.objects.create(link_external="https://openstax.org/2",
                                            link_text="Second", resource=faculty_resource_2,
                                            book_faculty_resource=book)

        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics-not-hidden')
        self.assertEqual(len(response.data['book_faculty_resources']), 2)

    def test_audiobook_link_field(self):
        """Test that audiobook_link can be set and is included in API responses"""
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            audiobook_url = 'https://example.com/audiobook'
            book = Book(title="University Physics",
                        slug="university-physics-audio",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_book_id='a0ZU0000008pyvQMAQ',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale,
                        audiobook_link=audiobook_url
                        )
            book_index.add_child(instance=book)

            # Verify the audiobook_link was saved
            self.assertEqual(book.audiobook_link, audiobook_url)

            # Verify it's included in API response
            response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics-audio')
            self.assertEqual(response.data['audiobook_link'], audiobook_url)


class BookAdminListingTests(TestCase):
    def test_book_listing_defaults_to_title_order(self):
        from books.wagtail_hooks import BookListingIndexView

        self.assertEqual(BookListingIndexView.default_ordering, "title")


class BookPreviewTests(TestCase):
    """Book preview must redirect to the headless frontend (/details/books/<slug>),
    not render the raw page.html fallback. See openstax.preview.FrontendPreviewMixin.
    """

    @patch('books.models.Book.get_url_parts')
    def test_book_preview_redirects_to_frontend(self, mock_get_url_parts):
        mock_get_url_parts.return_value = (1, 'http://dev.openstax.org', '/details/books/my-book')
        book = Book()
        response = book.serve_preview(None, 'some-mode')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.url.startswith('http://'))
        self.assertEqual(response.url, '/details/books/my-book/?preview=some-mode')

    @patch('books.models.Book.get_url_parts')
    def test_book_preview_falls_back_when_no_site(self, mock_get_url_parts):
        mock_get_url_parts.return_value = None
        book = Book()
        with patch('wagtail.models.Page.serve_preview') as mock_super:
            mock_super.return_value = 'fallback'
            result = book.serve_preview(None, 'some-mode')
        self.assertEqual(result, 'fallback')
