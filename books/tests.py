import vcr

from wagtail.tests.utils import WagtailPageTests
from wagtail.core.models import Page

import snippets.models
from pages.models import HomePage
from books.models import BookIndex, Book
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.documents.models import Document
import datetime


class BookTests(WagtailPageTests):

    def setUp(self):
        pass

    @classmethod
    def setUpTestData(cls):
        # create root page
        root_page = Page.objects.get(title="Root")
        # create homepage
        homepage = HomePage(title="Hello World",
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

        test_image = SimpleUploadedFile(name='openstax.png', content=open("oxauth/static/images/openstax.png", 'rb').read())
        cls.test_doc = Document.objects.create(title='Test Doc', file=test_image)

        cls.book_index = Page.objects.get(id=book_index.id)

    def test_can_create_book(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_name='University Physics',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'University Physics (Calc)')

    def test_can_create_ap_book(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Prealgebra",
                        slug="prealgebra",
                        salesforce_abbreviation='Biology',
                        salesforce_name='Biology',
                        description="This is Biology. Next, you learn Biology!",
                        is_ap=True,
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'Biology')


    def test_can_create_book_without_cnx_id(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Prealgebra",
                        slug="prealgebra",
                        salesforce_abbreviation='Prealgebra',
                        salesforce_name='Prealgebra',
                        description="This is Prealgebra. Next, you learn Algebra!",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')

    def test_only_numbers_for_price(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="Prealgebra",
                    slug="prealgebra",
                    salesforce_abbreviation='College Algebra',
                    salesforce_name='College Algebra',
                    description="This is College Algebra. Next, you learn Algebra!",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=root_page.locale
                    )
            book_index.add_child(instance=book)
            self.assertEqual(book.salesforce_abbreviation, 'College Algebra')

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(BookIndex, {
            Book
        })

    def test_cannot_create_book_under_homepage(self):
        self.assertCanNotCreateAt(HomePage, Book)

    def test_slashless_apis_are_good(self):
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/books')
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/books/slug')

    def test_can_create_book_with_cc_license(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/books.yaml'):
            book_index = BookIndex.objects.all()[0]
            root_page = Page.objects.get(title="Root")
            book = Book(title="University Physics",
                        slug="university-physics",
                        cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                        salesforce_abbreviation='University Physics (Calc)',
                        salesforce_name='University Physics  (Calc)',
                        description="Test Book",
                        cover=self.test_doc,
                        title_image=self.test_doc,
                        publish_date=datetime.date.today(),
                        locale=root_page.locale,
                        license_name='Creative Commons Attribution License',
                        )
            book_index.add_child(instance=book)
            self.assertEqual(book.license_url, 'https://creativecommons.org/licenses/by/4.0/')
