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

    def test_get_physics_authors(self):
        authors = get_authors('031da8d3-b525-429c-80cf-6c8ed997733a', 'College Physics')
        self.assertEqual(authors[0].name, 'Paul Peter Urone')

    def test_get_sociology_authors(self):
        authors = get_authors('02040312-72c8-441e-a685-20e9333f3e1d', 'Introduction to Sociology 2e')
        self.assertEqual(authors[0].name, 'Heather Griffiths')

    def test_get_polish_authors(self):
        authors = get_authors('4eaa8f03-88a8-485a-a777-dd3602f6c13e', 'Fizyka dla szkół wyższych. Tom 1')
        self.assertEqual(authors[0].name, 'Samuel J. Ling')

    def test_get_chem_atoms_authors(self):
        authors = get_authors('4539ae23-1ccc-421e-9b25-843acbb6c4b0', 'Chemistry: Atoms First')
        self.assertEqual(authors[0].name, 'Paul Flowers')

    def test_get_psychology_authors(self):
        authors = get_authors('4abf04bf-93a0-45c3-9cbc-2cefd46e68cc', 'Psychology')
        self.assertEqual(authors[0].name, 'Rose M. Spielman (Content Lead)')

    def test_get_econ_authors(self):
        authors = get_authors('69619d2b-68f0-44b0-b074-a9b2bf90b2c6', 'Principles of Economics')
        self.assertEqual(authors[0].name, 'Timothy Taylor')

    def test_get_biology_authors(self):
        authors = get_authors('185cbf87-c72e-48f5-b51e-f14f21b5eabd', 'Biology')
        self.assertEqual(authors[0].name, 'Yael Avissar (Cell Biology)')

    def test_get_anatomy_authors(self):
        authors = get_authors('14fb4ad7-39a1-4eee-ab6e-3ef2482e3e22', 'Anatomy & Physiology')
        self.assertEqual(authors[0].name, 'J. Gordon Betts')

    def test_get_ap_microecon_authors(self):
        #returns nothing because of incorrect markup in the Preface
        get_authors('ca344e2d-6731-43cd-b851-a7b3aa0b37aa', 'Principles of Microeconomics for AP® Courses')

    def test_get_us_history_authors(self):
        authors = get_authors('a7ba2fb8-8925-4987-b182-5f4429d48daa', 'U.S. History')
        self.assertEqual(authors[0].name, 'P. Scott Corbett')

    def test_get_calculus1_authors(self):
        authors = get_authors('8b89d172-2927-466f-8661-01abc7ccdba4', 'Calculus Volume 1')
        self.assertEqual(authors[0].name,'Gilbert Strang')
