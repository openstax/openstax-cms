from wagtail.tests.utils import WagtailPageTests
from wagtail.core.models import Page
from pages.models import HomePage
from books.models import BookIndex, Book
from snippets.models import Subject
from books.functions import get_authors


class BookTests(WagtailPageTests):
    def setUp(self):
        pass

    def test_can_create_book_index(self):
        #create root page
        root_page = Page.objects.get(title="Root")
        #create homepage
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        #add homepage to root page
        root_page.add_child(instance=homepage)
        #create book index page
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               )
        #add book index to homepage
        homepage.add_child(instance=book_index)

        retrieved_page = Page.objects.get(id=book_index.id)
        self.assertEqual(retrieved_page.title, "Book Index")

    def test_can_create_book(self):
        subject = Subject(name="Science")

        book = Book(cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_abbreviation='University Phys (Calc)',
                    salesforce_name='University Physics',
                    subject=subject,
                    description="Test Book",
                    )
        self.assertEqual(book.salesforce_abbreviation, 'University Phys (Calc)')

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(BookIndex, {
            Book
        })

    def test_get_authors(self):
        subject = Subject(name="Science")
        book = Book(cnx_id='4eaa8f03-88a8-485a-a777-dd3602f6c13e',
                    salesforce_abbreviation='College Physics',
                    salesforce_name='College Physics',
                    title="Fizyka dla szkół wyższych. Tom 1",
                    subject=subject,
                    description="Test Book",
                    )
        get_authors(book)

    def test_get_sociology_authors(self):
        subject = Subject(name="Science")
        book = Book(cnx_id='02040312-72c8-441e-a685-20e9333f3e1d',
                    salesforce_abbreviation='College Physics',
                    salesforce_name='College Physics',
                    title="Introduction to Sociology 2e",
                    subject=subject,
                    description="Test Book",
                    )
        get_authors(book)

    def test_get_polish_authors(self):
        subject = Subject(name="Science")
        book = Book(cnx_id='4eaa8f03-88a8-485a-a777-dd3602f6c13e',
                    salesforce_abbreviation='College Physics',
                    salesforce_name='College Physics',
                    title="Fizyka dla szkół wyższych. Tom 1",
                    subject=subject,
                    description="Test Book",
                    )
        get_authors(book)

    def test_get_chem_atoms_authors(self):
        subject = Subject(name="Science")
        book = Book(cnx_id='4539ae23-1ccc-421e-9b25-843acbb6c4b0',
                    salesforce_abbreviation='College Physics',
                    salesforce_name='College Physics',
                    title="Chemistry: Atoms First",
                    subject=subject,
                    description="Test Book",
                    )
        get_authors(book)

    def test_get_psychology_authors(self):
        subject = Subject(name="Science")
        book = Book(cnx_id='4abf04bf-93a0-45c3-9cbc-2cefd46e68cc',
                    salesforce_abbreviation='College Physics',
                    salesforce_name='College Physics',
                    title="Psychology",
                    subject=subject,
                    description="Test Book",
                    )
        get_authors(book)
