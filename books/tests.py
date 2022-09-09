import json
from collections import OrderedDict

from django.forms import model_to_dict
from wagtail.tests.utils import WagtailPageTests
from wagtail.images.tests.utils import Image, get_test_image_file
from wagtail.documents.models import Document
from wagtail.core.models import Page

import books
import snippets.models
from pages.models import HomePage
from books.models import BookIndex, Book, BookFacultyResources
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime


class BookTests(WagtailPageTests):

    def setUp(self):
        # create root page
        self.root_page = Page.objects.get(title="Root")
        # create homepage
        self.homepage = HomePage(title="Hello World", slug="hello-world")
        # add homepage to root page
        self.root_page.add_child(instance=self.homepage)
        # create book index page
        self.book_index = BookIndex(title="Book Index",
                                   page_description="Test",
                                   dev_standard_1_description="Test",
                                   dev_standard_2_description="Test",
                                   dev_standard_3_description="Test",
                                   dev_standard_4_description="Test",
                                   )
        # add book index to homepage
        self.homepage.add_child(instance=self.book_index)

        self.book = Book(title="University Physics",
                        slug="university-physics",
                        salesforce_abbreviation='University Phys (Calc)',
                        salesforce_name='University Physics',
                        description="Test Book",
                        publish_date=datetime.date.today(),
                        locale=self.root_page.locale,
                        license_name='Creative Commons Attribution License'
                        )
        self.book_index.add_child(instance=self.book)

    def test_can_create_book(self):
        self.assertEqual(self.book.salesforce_abbreviation, 'University Phys (Calc)')

    # TODO: not sure what this is testing... likely not needed
    def test_can_create_ap_book(self):
        self.assertEqual(self.book.salesforce_abbreviation, 'University Phys (Calc)')

    def test_can_create_book_without_cnx_id(self):
        self.book.cnx_id = None
        self.book.save()
        self.assertEqual(self.book.salesforce_abbreviation, 'University Phys (Calc)')

    # TODO: again.. not sure what this is testing
    def test_only_numbers_for_price(self):
        self.assertEqual(self.book.salesforce_abbreviation, 'University Phys (Calc)')

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(BookIndex, { Book })

    def test_cannot_create_book_under_homepage(self):
        self.assertCanNotCreateAt(HomePage, Book)

    def test_slashless_apis_are_good(self):
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/books')
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/books/slug')

    def test_can_create_book_with_cc_license(self):
        self.book.license_name = 'Creative Commons Attribution License'
        self.book.save()
        self.assertEqual(self.book.license_url, 'https://creativecommons.org/licenses/by/4.0/')


    def test_faculty_resources_available_or_not(self):
        faculty_resource = snippets.models.FacultyResource(heading="Instructor Getting Started Guide",
                                                           description="<p data-block-key=\"6o2yl\">Download our helpful guide to all things OpenStax.<br/></p>",
                                                           unlocked_resource=False,
                                                           creator_fest_resource=False)
        faculty_resource.save()

        book_faculty_resource = BookFacultyResources.objects.create(link_external="https://openstax.org", link_text="Go!",resource=faculty_resource,book_faculty_resource=self.book)
        book_faculty_resource.save()

        # run test without flag
        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics')
        self.assertEqual(response.data['book_faculty_resources'][0]['link_external'], 'https://openstax.org')
        # check book data is cleared out
        self.assertEqual(response.data['book_faculty_resources'][0]['book_faculty_resource'],{})

        # run test with flag
        response = self.client.get('/apps/cms/api/books/resources/?slug=university-physics&x=y')
        self.assertEqual(response.data['book_faculty_resources'][0]['link_external'], '')
