import datetime
import json

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.test.utils import WagtailPageTestCase

from books.models import Book, BookIndex, BookSubjects
from news.models import NewsArticle, NewsIndex
from pages.models import RootPage
from snippets.models import Subject
from webinars.models import Webinar


class SearchViewTests(WagtailPageTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        root_page = Page.objects.get(title="Root")
        homepage = RootPage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)
        news_index = NewsIndex(title="News Index")
        homepage.add_child(instance=news_index)
        cls.news_index = Page.objects.get(id=news_index.id)
        book_index = BookIndex(title="Book Index", page_description="Test",
                               dev_standard_1_description="Test", dev_standard_2_description="Test",
                               dev_standard_3_description="Test", dev_standard_4_description="Test")
        homepage.add_child(instance=book_index)
        cls.book_index = Page.objects.get(id=book_index.id)

    def setUp(self):
        self.nova = Subject(name="Nova", page_content="x", seo_title="x", search_description="x")
        self.nova.save()

        news_index = NewsIndex.objects.all()[0]
        for i in range(7):
            article = NewsArticle(
                title=f"Cryostax Report {i}",
                slug=f"cryostax-{i}",
                date=timezone.now() - datetime.timedelta(days=i),
                heading=f"Cryostax heading {i}",
                author="OpenStax",
                body=json.dumps([{"type": "paragraph", "value": f"<p>cryostax findings {i}</p>"}]),
                article_subjects=json.dumps(
                    [{'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': self.nova.id, 'featured': False}}]}]
                ),
                content_types=json.dumps([]),
                collections=json.dumps([]),
            )
            news_index.add_child(instance=article)

        book_index = BookIndex.objects.all()[0]
        self.book_nova = Book(title="Cryostax Biology", slug="cryostax-biology",
                              description="A cryostax textbook about biology.",
                              publish_date=datetime.date.today(), locale=book_index.locale)
        book_index.add_child(instance=self.book_nova)
        BookSubjects.objects.create(book_subject=self.book_nova, subject=self.nova)

        self.book_no_subject = Book(title="Cryostax Chemistry", slug="cryostax-chemistry",
                                    description="A cryostax textbook about chemistry.",
                                    publish_date=datetime.date.today(), locale=book_index.locale)
        book_index.add_child(instance=self.book_no_subject)

        self.book_retired = Book(title="Cryostax Retired", slug="cryostax-retired",
                                 description="A cryostax textbook that is retired.",
                                 book_state='retired', publish_date=datetime.date.today(),
                                 locale=book_index.locale)
        book_index.add_child(instance=self.book_retired)

        self.webinar = Webinar(
            title="Cryostax Webinar",
            start=timezone.now(),
            end=timezone.now(),
            description="A cryostax webinar description.",
            speakers="Ana, Bo",
            registration_url="https://example.com",
            registration_link_text="Register",
            webinar_subjects=json.dumps([]),
            webinar_collections=json.dumps([]),
        )
        self.webinar.save()

        # The DB search backend doesn't auto-index in tests (see news/tests.py's
        # identical helper) — .search() sees nothing until we add rows ourselves.
        # Books/webinars are indexed regardless of live/retired state, same as
        # production reindexing would do — the retired-book exclusion is a
        # query-time .exclude(), not something the index itself enforces.
        backend = get_search_backend()
        for a in NewsArticle.objects.live():
            backend.add(a)
        for b in Book.objects.all():
            backend.add(b)
        for w in Webinar.objects.all():
            backend.add(w)

    def test_envelope_shape(self):
        response = self.client.get('/apps/cms/api/search/v2/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('query', data)
        news = data['sources']['news']
        self.assertEqual(set(news), {'page', 'page_size', 'total', 'next', 'previous', 'results'})

    def test_page_size_is_honoured(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'page_size': 2})
        news = response.json()['sources']['news']
        self.assertEqual(news['page_size'], 2)
        self.assertEqual(len(news['results']), 2)

    def test_page_size_is_capped_at_max(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'page_size': 9999})
        news = response.json()['sources']['news']
        self.assertEqual(news['page_size'], 50)
        self.assertEqual(news['total'], 7)

    def test_sources_param_filters_to_requested_key(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'sources': 'news'})
        self.assertEqual(set(response.json()['sources']), {'news'})

    def test_unknown_source_key_is_ignored_not_an_error(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'sources': 'bogus'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['sources'], {})

    def test_legacy_route_still_returns_bare_array(self):
        response = self.client.get('/apps/cms/api/search/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_q_facet_and_pagination_compose(self):
        # Scoped to sources=news so a shorter source running out of pages can't
        # be what this test observes.
        response = self.client.get('/apps/cms/api/search/v2/', {
            'q': 'cryostax', 'subjects': 'Nova', 'sort': 'newest', 'page': 2, 'page_size': 3,
            'sources': 'news',
        })
        news = response.json()['sources']['news']
        self.assertEqual(news['total'], 7)
        self.assertEqual(news['page'], 2)
        # newest-first (i=0 is today, i=6 is 6 days ago); page 2 of size 3 is i=3,4,5.
        self.assertEqual([r['slug'] for r in news['results']], ['cryostax-3', 'cryostax-4', 'cryostax-5'])

    def test_source_running_out_of_pages_does_not_fail_the_envelope(self):
        """One short source must not 404 the sources that do have that page."""
        response = self.client.get('/apps/cms/api/search/v2/', {
            'q': 'cryostax', 'subjects': 'Nova', 'sort': 'newest', 'page': 2, 'page_size': 3,
        })
        self.assertEqual(response.status_code, 200)
        sources = response.json()['sources']
        self.assertEqual([r['slug'] for r in sources['news']['results']],
                         ['cryostax-3', 'cryostax-4', 'cryostax-5'])
        self.assertEqual(sources['books']['results'], [])
        self.assertGreater(sources['books']['total'], 0)

    def test_book_and_webinar_hits_appear_under_their_own_source_keys(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'q': 'cryostax'})
        sources = response.json()['sources']
        self.assertGreater(sources['books']['total'], 0)
        self.assertGreater(sources['webinars']['total'], 0)

    def test_sources_books_returns_only_books(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'sources': 'books'})
        self.assertEqual(set(response.json()['sources']), {'books'})

    def test_book_subject_filter_works(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'sources': 'books', 'subjects': 'Nova'})
        books = response.json()['sources']['books']
        self.assertEqual(books['total'], 1)
        self.assertEqual(books['results'][0]['slug'], 'books/cryostax-biology')

    def test_retired_book_is_excluded(self):
        response = self.client.get('/apps/cms/api/search/v2/', {'sources': 'books', 'q': 'cryostax'})
        books = response.json()['sources']['books']
        self.assertEqual(books['total'], 2)
        self.assertNotIn('books/cryostax-retired', [r['slug'] for r in books['results']])

    def test_legacy_webinar_search_route_is_untouched(self):
        """webinars/search.py and its route are not part of this PR - just
        confirming the new Webinar.search_fields/index.Indexed additions
        don't disturb its independent hand-rolled Postgres query."""
        response = self.client.get('/apps/cms/api/webinars/search/', {'q': 'cryostax'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(set(data[0]), {
            'id', 'title', 'description', 'start', 'end', 'speakers', 'spaces_remaining',
            'registration_url', 'registration_link_text', 'display_on_tutor_page', 'subjects', 'collections',
        })
