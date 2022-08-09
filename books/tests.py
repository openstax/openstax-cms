import json

from wagtail.tests.utils import WagtailPageTests
from wagtail.core.models import Page

import books
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
        book_index = BookIndex.objects.all()[0]
        root_page = Page.objects.get(title="Root")
        book = Book(title="University Physics",
                    slug="university-physics",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_abbreviation='University Phys (Calc)',
                    salesforce_name='University Physics',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=root_page.locale
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'University Phys (Calc)')

    def test_can_create_ap_book(self):
        book_index = BookIndex.objects.all()[0]
        root_page = Page.objects.get(title="Root")
        book = Book(title="Prealgebra",
                    slug="prealgebra",
                    salesforce_abbreviation='Prealgebra',
                    salesforce_name='Prealgebra',
                    description="This is Prealgebra. Next, you learn Algebra!",
                    is_ap=True,
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=root_page.locale
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')


    def test_can_create_book_without_cnx_id(self):
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
        book_index = BookIndex.objects.all()[0]
        root_page = Page.objects.get(title="Root")
        book = Book(title="University Physics",
                    slug="university-physics",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_abbreviation='University Phys (Calc)',
                    salesforce_name='University Physics',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=root_page.locale,
                    license_name='Creative Commons Attribution License',
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.license_url, 'https://creativecommons.org/licenses/by/4.0/')


class ResourceTests(WagtailPageTests):
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

        test_image = SimpleUploadedFile(name='openstax.png',
                                        content=open("oxauth/static/images/openstax.png", 'rb').read())
        cls.test_doc = Document.objects.create(title='Test Doc', file=test_image)

        cls.book_index = Page.objects.get(id=book_index.id)

    def test_faculty_resources_available(self):
        book_index = BookIndex.objects.all()[0]
        root_page = Page.objects.get(title="Root")
        faculty_resource = snippets.models.FacultyResource(heading="Instructor Getting Started Guide",
                                                           description="<p data-block-key=\"6o2yl\">Download our helpful guide to all things OpenStax.<br/></p>",
                                                           unlocked_resource=True,
                                                           creator_fest_resource=False)
        faculty_resource.save()
        resource = books.models.FacultyResources(link_external="https://openstax.org",
                                                 link_text="Go!",
                                                 coming_soon_text=None,
                                                 video_reference_number=None,
                                                 updated=None,
                                                 featured=False,
                                                 k12=False,
                                                 print_link=None,
                                                 resource_id=faculty_resource.id)
        resource.save()

        # book_faculty_resource = books.models.BookFacultyResources(faculty_resources_ptr_id=resource.id,
        #                                                           sort_order=0,
        #                                                           book_faculty_resource_id=book.id)

        book = Book(title="University Physics",
                    slug="university-physics",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_abbreviation='University Phys (Calc)',
                    salesforce_name='University Physics',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=root_page.locale,
                    license_name='Creative Commons Attribution License',
                    book_faculty_resources={resource}
                    )
        #book.save()
        book_index.add_child(instance=book)

        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics')
        self.assertContains(response, 'https://openstax.org')
