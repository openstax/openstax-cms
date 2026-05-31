import datetime
import json

from django.utils import timezone
from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page
from pages.models import HomePage
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from unittest.mock import MagicMock
from news.models import NewsIndex, NewsArticle, PressIndex, PressRelease
from snippets.models import Subject, BlogContentType, BlogCollection


class NewsTests(WagtailPageTestCase, TestCase):
    def setUp(self):
        # create collections
        self.learning = BlogCollection(name='Teaching and Learning', description='this is a collection')
        self.learning.save()
        learning_id = self.learning.id

        self.updates = BlogCollection(name='OpenStax Updates', description='this is a collection')
        self.updates.save()
        update_id = self.updates.id
        # create content types
        self.case_study = BlogContentType(content_type='Case Study')
        self.case_study.save()
        case_study_id = self.case_study.id

        self.video = BlogContentType(content_type='Video')
        self.video.save()
        video_id = self.video.id
        # create subjects
        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                            search_description="Math page description.")
        self.math.save()
        math_id = self.math.id

        self.economics = Subject(name="Economics", page_content="Economics page content.",
                                 seo_title="Economics SEO Title",
                                 search_description="Economics page description.")
        self.economics.save()
        economics_id = self.economics.id
        # create news articles
        news_index = NewsIndex.objects.all()[0]
        self.article = NewsArticle(title="Article 1",
                                   slug="article",
                                   date=timezone.now(),
                                   heading="Sample Article",
                                   subheading="Sample Subheading",
                                   author="OpenStax",
                                   body=json.dumps(
                                       [
                                           {"type": "paragraph",
                                            "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                       ]
                                   ),
                                   article_subjects=json.dumps(
                                       [
                                           {'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': math_id, 'featured': False}}]}
                                       ]
                                   ),
                                   content_types=json.dumps(
                                       [
                                           {'type': 'content_type', 'value': [
                                               {'type': 'item', 'value': {'content_type': case_study_id}}]}
                                       ]
                                   ),
                                   collections=json.dumps(
                                       [
                                           {'type': 'collection', 'value': [
                                               {'type': 'item', 'value': {'collection': learning_id, 'featured': False, 'popular': False}}]}
                                       ]
                                   ))
        news_index.add_child(instance=self.article)
        self.article2 = NewsArticle(title="Article 2",
                                    slug="article2",
                                    date=timezone.now(),
                                    heading="Sample Article 2",
                                    subheading="Sample Subheading 2",
                                    author="OpenStax",
                                    body=json.dumps(
                                        [
                                            {"type": "paragraph",
                                             "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                        ]
                                    ),
                                    article_subjects=json.dumps(
                                        [
                                            {'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': economics_id, 'featured': False}}]}
                                        ]
                                    ),
                                    content_types=json.dumps(
                                        [
                                            {'type': 'content_type', 'value': [
                                                {'type': 'item', 'value': {'content_type': video_id}}]}
                                        ]
                                    ),
                                    collections=json.dumps(
                                        [
                                            {'type': 'collection', 'value': [
                                                {'type': 'item', 'value': {'collection': update_id, 'featured': False,
                                                                           'popular': False}}]}
                                        ]
                                    ))
        news_index.add_child(instance=self.article2)
        self.article3 = NewsArticle(title="Article 3",
                                    slug="article3",
                                    date=timezone.now(),
                                    heading="Sample Article 3",
                                    subheading="Sample Subheading 3",
                                    author="OpenStax",
                                    body=json.dumps(
                                        [
                                            {"type": "paragraph",
                                             "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                        ]
                                    ),
                                    article_subjects=json.dumps(
                                        [
                                            {'type': 'subject', 'value': [{'type': 'item','value': {'subject': math_id,'featured': False}}]}
                                        ]
                                    ),
                                    content_types=json.dumps(
                                        [
                                            {'type': 'content_type', 'value': [
                                                {'type': 'item', 'value': {'content_type': case_study_id}}]}
                                        ]
                                    ),
                                    collections=json.dumps(
                                        [
                                            {'type': 'collection', 'value': [
                                                {'type': 'item', 'value': {'collection': update_id, 'featured': False,
                                                                           'popular': False}}]}

                                        ]
                                    ))
        news_index.add_child(instance=self.article3)
        self.article4 = NewsArticle(title="Article 4",
                                    slug="article4",
                                    date=timezone.now(),
                                    heading="Sample Article 4",
                                    subheading="Sample Subheading 4",
                                    author="OpenStax",
                                    body=json.dumps(
                                        [
                                            {"type": "paragraph",
                                             "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                        ]
                                    ),
                                    article_subjects=json.dumps(
                                        [
                                            {'type': 'subject', 'value': [
                                                {'type': 'item', 'value': {'subject': math_id, 'featured': False}}]}
                                        ]
                                    ),
                                    content_types=json.dumps(
                                        [
                                            {'type': 'content_type', 'value': [
                                                {'type': 'item', 'value': {'content_type': case_study_id}}]}
                                        ]
                                    ),
                                    collections=json.dumps(
                                        [
                                            {'type': 'collection', 'value': [
                                                {'type': 'item', 'value': {'collection': update_id, 'featured': False,
                                                                           'popular': False}}]}

                                        ]
                                    ),
                                    live=False)
        news_index.add_child(instance=self.article4)

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
        news_index = NewsIndex(title="News Index")

        homepage.add_child(instance=news_index)

        cls.news_index = Page.objects.get(id=news_index.id)

    def test_bad_slug_returns_404(self):
        response = self.client.get('/apps/cms/api/news/bad-slug/', format='json')
        self.assertEqual(response.status_code, 404)

    def test_slashless_apis_are_good(self):
        original_news_index_all = NewsIndex.objects.all
        original_press_index_all = PressIndex.objects.all
        original_news_article_get = NewsArticle.objects.get
        original_press_release_get = PressRelease.objects.get
        self.addCleanup(setattr, NewsIndex.objects, 'all', original_news_index_all)
        self.addCleanup(setattr, PressIndex.objects, 'all', original_press_index_all)
        self.addCleanup(setattr, NewsArticle.objects, 'get', original_news_article_get)
        self.addCleanup(setattr, PressRelease.objects, 'get', original_press_release_get)

        NewsIndex.objects.all = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/news')

        PressIndex.objects.all = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/press')

        NewsArticle.objects.get = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/news/slug')

        PressRelease.objects.get = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/press/slug')

    def test_search_subject_only(self):
        response = self.client.get('/apps/cms/api/search/',{'subjects': 'Math'})
        self.assertContains(response, 'Math')

    def test_search_live_subject_only(self):
        response = self.client.get('/apps/cms/api/search/',{'subjects': 'Math'})
        self.assertNotContains(response, 'Article 4')

    def test_search_blog_collection(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates'})
        self.assertContains(response, 'OpenStax Updates')

    def test_search_live_blog_collection(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates'})
        self.assertNotContains(response, 'Article 4')

    def test_search_blog_content_type(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Video'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Video')

    def test_search_live_blog_content_type(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Case Study'})
        self.assertNotContains(response, 'Article 4')

    def test_search_blogcollection_and_subject(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'subjects': 'Economics'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Economics')

    def test_search_blog_content_type_and_subject(self):
        # AND semantics: collection=OpenStax Updates AND type=Case Study AND subject=Economics.
        # No fixture article satisfies all three (Article 2 is Updates/Video/Economics,
        # Article 3 is Updates/Case Study/Math), so the correct result is empty.
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Case Study', 'subjects': 'Economics'})
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_search_blog_multiple_content_type_and_subject(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Case Study,Video', 'subjects': 'Economics,Math'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Case Study')
        self.assertContains(response, 'Economics')

    def test_search_two_blog_content_types(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Video,Case Study'})
        self.assertContains(response, 'Video')
        self.assertContains(response, 'Case Study')

    def test_search_blog_collection_and_two_subjects(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'subjects': 'Economics,Math'})
        self.assertContains(response, 'Economics')
        self.assertContains(response, 'Math')

    def test_subject_name_is_searchable(self):
        """Subject name (e.g. 'Math') should be findable via Wagtail .search() once indexed."""
        from wagtail.search.backends import get_search_backend
        backend = get_search_backend()
        for a in NewsArticle.objects.live():
            backend.add(a)
        results = NewsArticle.objects.live().search('Math')
        result_list = list(results)
        self.assertTrue(len(result_list) > 0, "No results for 'Math' — subject names are not indexed")
        names = [s['name'] for s in result_list[0].blog_subjects]
        self.assertIn('Math', names)

    def _populate_search_index(self):
        """Add all live NewsArticles to the Wagtail search backend so .search() returns them in-test."""
        from wagtail.search.backends import get_search_backend
        backend = get_search_backend()
        for a in NewsArticle.objects.live():
            backend.add(a)

    def test_keyword_and_subject_compose(self):
        """q + subjects must AND-compose: only keyword matches that also carry the subject are returned."""
        news_index = NewsIndex.objects.all()[0]
        math_id = self.math.id
        economics_id = self.economics.id

        # Math article containing the unique keyword
        math_kw = NewsArticle(
            title="Quasar Math Study",
            slug="quasar-math",
            date=timezone.now(),
            heading="Quasar heading",
            subheading="Quasar sub",
            author="OpenStax",
            body=json.dumps([{"type": "paragraph", "value": "<p>This study about quasarterm covers math.</p>"}]),
            article_subjects=json.dumps(
                [{'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': math_id, 'featured': False}}]}]
            ),
            content_types=json.dumps([]),
            collections=json.dumps([]),
        )
        news_index.add_child(instance=math_kw)

        # Economics article containing the SAME unique keyword (must be excluded by subjects=Math)
        econ_kw = NewsArticle(
            title="Quasar Economics Study",
            slug="quasar-econ",
            date=timezone.now(),
            heading="Quasar heading",
            subheading="Quasar sub",
            author="OpenStax",
            body=json.dumps([{"type": "paragraph", "value": "<p>This study about quasarterm covers economics.</p>"}]),
            article_subjects=json.dumps(
                [{'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': economics_id, 'featured': False}}]}]
            ),
            content_types=json.dumps([]),
            collections=json.dumps([]),
        )
        news_index.add_child(instance=econ_kw)

        self._populate_search_index()

        response = self.client.get('/apps/cms/api/search/', {'q': 'quasarterm', 'subjects': 'Math'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        slugs = [item['slug'] for item in data]

        self.assertIn('quasar-math', slugs, "Math keyword match should be present")
        self.assertNotIn('quasar-econ', slugs, "Economics keyword match must be excluded by subjects=Math")
        # Article 1 has subject Math but does NOT contain the keyword: must be excluded
        # (proves we compose with the keyword result, not just filter all Math articles).
        self.assertNotIn('article', slugs, "Math article without the keyword must not appear")

    def test_sort_newest_overrides_relevance(self):
        """q + sort=newest returns results in non-increasing date order."""
        news_index = NewsIndex.objects.all()[0]

        older = NewsArticle(
            title="Photosynthesis Explained",
            slug="photo-older",
            date=timezone.now() - datetime.timedelta(days=30),
            heading="Photosynthesis heading",
            subheading="About photosynthesis",
            author="OpenStax",
            body=json.dumps([{"type": "paragraph", "value": "<p>Photosynthesis in depth.</p>"}]),
            article_subjects=json.dumps([]),
            content_types=json.dumps([]),
            collections=json.dumps([]),
        )
        news_index.add_child(instance=older)

        newer = NewsArticle(
            title="Topics in Biology",
            slug="photo-newer",
            date=timezone.now(),
            heading="Biology heading",
            subheading="Various biology topics",
            author="OpenStax",
            body=json.dumps(
                [{"type": "paragraph",
                  "value": "<p>Photosynthesis is a process. Photosynthesis uses light. "
                           "Photosynthesis makes sugar.</p>"}]
            ),
            article_subjects=json.dumps([]),
            content_types=json.dumps([]),
            collections=json.dumps([]),
        )
        news_index.add_child(instance=newer)

        self._populate_search_index()

        response = self.client.get('/apps/cms/api/search/', {'q': 'photosynthesis', 'sort': 'newest'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        dates = [item['date'] for item in data]
        self.assertEqual(dates, sorted(dates, reverse=True),
                         "sort=newest must return results in non-increasing date order")

    def test_keyword_search_orders_by_relevance_not_date(self):
        """Title match (older date) should rank above body-only match (newer date)."""
        news_index = NewsIndex.objects.all()[0]

        # Article A: term in TITLE, older date — should rank highest
        article_a = NewsArticle(
            title="Thermodynamics Explained",
            slug="thermo-title-match",
            date=timezone.now() - datetime.timedelta(days=30),
            heading="Thermodynamics heading",
            subheading="All about thermodynamics",
            author="OpenStax",
            body=json.dumps(
                [
                    {"type": "paragraph",
                     "value": "<p>This article covers thermodynamics in depth.</p>"}
                ]
            ),
            article_subjects=json.dumps([]),
            content_types=json.dumps([]),
            collections=json.dumps([]),
        )
        news_index.add_child(instance=article_a)

        # Article B: term only in BODY (3 times to clear 0.3 threshold), newer date
        article_b = NewsArticle(
            title="Physics Topics",
            slug="thermo-body-only",
            date=timezone.now(),
            heading="Physics heading",
            subheading="Various physics topics",
            author="OpenStax",
            body=json.dumps(
                [
                    {"type": "paragraph",
                     "value": "<p>Thermodynamics is a branch of physics. "
                              "Thermodynamics deals with heat and energy. "
                              "Thermodynamics has many practical applications.</p>"}
                ]
            ),
            article_subjects=json.dumps([]),
            content_types=json.dumps([]),
            collections=json.dumps([]),
        )
        news_index.add_child(instance=article_b)

        self._populate_search_index()

        response = self.client.get('/apps/cms/api/search/', {'q': 'thermodynamics'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        slugs = [item['slug'] for item in data]

        self.assertIn('thermo-title-match', slugs, "Title-match article not found in results (may not clear 0.3 threshold)")
        self.assertIn('thermo-body-only', slugs, "Body-only article not found in results (may not clear 0.3 threshold)")

        self.assertLess(
            slugs.index('thermo-title-match'),
            slugs.index('thermo-body-only'),
            "Title-match (older) article should appear before body-only (newer) article when ordered by relevance"
        )


class PressTests(WagtailPageTestCase):
    def setUp(self):
        press_index = PressIndex.objects.all()[0]
        self.press_release = PressRelease(title='Press release',
                                     date=datetime.datetime.now(),
                                     author='someone',
                                     heading='heading',
                                     excerpt='this is a press release',
                                     slug='press-release-1',
                                     path=' ',
                                     depth=1,
                                     body=json.dumps(
                                         [{"id": "ae6f048b-6eb5-42e7-844f-cfcd459f81b5", "type": "heading",
                                           "value": "Press release"},
                                          {"id": "a21bcbd4-fec4-432e-bf06-966d739c6de9", "type": "paragraph",
                                           "value": "<p data-block-key=\"wr6bg\">This is a test of a press release.</p><p data-block-key=\"d57h\">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"},
                                          {"id": "4d339739-131c-4547-954b-0787afdc4914", "type": "tagline",
                                           "value": "This is a test"}]
                                     )
                                     )
        press_index.add_child(instance=self.press_release)

    @classmethod
    def setUpTestData(cls):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)

        press_index = PressIndex(about='About press index',
                                 press_inquiry_phone='111-111-1111',
                                 press_inquiry_email='press@example.com',
                                 experts_heading='experts heading',
                                 experts_blurb='experts blurb',
                                 infographic_text='infographic text',
                                 title='Press Index',
                                 path=' ',
                                 slug='press',
                                 depth=1)
        # add book index to homepage
        homepage.add_child(instance=press_index)
        cls.press_index = Page.objects.get(id=press_index.id)

    def test_can_create_press_release(self):
        self.assertEqual(self.press_release.title, 'Press release')






