from wagtail.tests.utils import WagtailPageTests
from wagtail.core.models import Page
from pages.models import HomePage
from books.models import BookIndex, Book, BookAllies
#from snippets.models import Subject
from allies.models import Ally


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
                               )
        # add book index to homepage
        homepage.add_child(instance=book_index)

        cls.book_index = Page.objects.get(id=book_index.id)

    def test_can_create_book(self):
        book_index = BookIndex.objects.all()[0]
        book = Book(title="University Physics",
                    slug="university-physics",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_abbreviation='University Phys (Calc)',
                    salesforce_name='University Physics',
                    description="Test Book",
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'University Phys (Calc)')

    def test_can_create_ap_book(self):
        book_index = BookIndex.objects.all()[0]
        book = Book(title="Prealgebra",
                    slug="prealgebra",
                    salesforce_abbreviation='Prealgebra',
                    salesforce_name='Prealgebra',
                    description="This is Prealgebra. Next, you learn Algebra!",
                    is_ap=True
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')


    def test_can_create_book_without_cnx_id(self):
        book_index = BookIndex.objects.all()[0]
        book = Book(title="Prealgebra",
                    slug="prealgebra",
                    salesforce_abbreviation='Prealgebra',
                    salesforce_name='Prealgebra',
                    description="This is Prealgebra. Next, you learn Algebra!",
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')

    def test_can_create_coming_soon_book(self):
        book_index = BookIndex.objects.all()[0]
        book = Book(title="Prealgebra",
                    slug="prealgebra",
                    salesforce_abbreviation='Prealgebra',
                    salesforce_name='Prealgebra',
                    description="This is Prealgebra. Next, you learn Algebra!",
                    coming_soon=True
                    )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')

    def test_only_numbers_for_price(self):
        book_index = BookIndex.objects.all()[0]
        book = Book(title="Prealgebra",
                slug="prealgebra",
                salesforce_abbreviation='Prealgebra',
                salesforce_name='Prealgebra',
                description="This is Prealgebra. Next, you learn Algebra!",
                amazon_price=False
                )
        book_index.add_child(instance=book)
        self.assertEqual(book.salesforce_abbreviation, 'Prealgebra')

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(BookIndex, {
            Book
        })

    def test_cannot_create_book_under_homepage(self):
        self.assertCanNotCreateAt(HomePage, Book)

