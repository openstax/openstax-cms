from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page

import snippets.models
from pages.models import HomePage
from books.models import BookIndex, Book, BookFacultyResources
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from salesforce.tests import openstax_vcr as vcr
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
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
        self.assertCanNotCreateAt(HomePage, Book)

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

