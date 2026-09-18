import datetime
import json
import re
from .functions import remove_locked_links_detail, remove_locked_links_listing, build_document_url, build_image_url

from django.test import TestCase, SimpleTestCase, Client, RequestFactory, override_settings
from django.http import HttpResponse, HttpResponseNotFound
from django.core.files.uploadedfile import SimpleUploadedFile
from openstax.frontend_routes import form_route_heading
from openstax.middleware import CommonMiddlewareAppendSlashWithoutRedirect
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Locale, Page, PageViewRestriction, Site
from pages.models import (
    RootPage, FlexPage, FormHeadings, GeneralPage, InstitutionalPartnership,
)
from books.models import BookIndex, Book
from news.models import NewsIndex, NewsArticle
from salesforce.models import Adopter
from snippets.models import Subject, BlogContentType, BlogCollection
from wagtail.documents.models import Document


class TestClass(object):
    pass


@override_settings(ALLOWED_HOSTS=['*'], APPEND_SLASH=True)
class AppendSlashWithoutRedirectTest(SimpleTestCase):
    """Regression for the slash-less 404 bug.

    A URL whose slashed form resolves (e.g. ``/admin/pages``) must be served via
    the middleware's internal re-dispatch, not 404. Django's URL resolver matches
    on ``request.path_info``, so the middleware has to append the trailing slash
    there too -- updating only ``request.path`` left the re-dispatch resolving the
    original slash-less path, which 404'd.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def _redispatch_capture(self, path):
        # View layer 404s for the slash-less path, as the real resolver would,
        # which triggers Django's append-slash redirect that the middleware
        # converts into an internal re-dispatch.
        mw = CommonMiddlewareAppendSlashWithoutRedirect(
            lambda req: HttpResponseNotFound("nope")
        )
        captured = {}

        def fake_redispatch(request):
            captured["path"] = request.path
            captured["path_info"] = request.path_info
            return HttpResponse("ok")

        mw.handler.get_response = fake_redispatch
        request = self.factory.get(path)
        response = mw.process_response(request, HttpResponseNotFound("nope"))
        return response, captured

    def test_no_slash_url_redispatched_with_slash_on_path_info(self):
        response, captured = self._redispatch_capture("/admin/pages")
        # Re-dispatch happened instead of staying a 404 ...
        self.assertEqual(response.status_code, 200)
        # ... and the slash is on path_info (what the resolver matches), not just path.
        self.assertEqual(captured["path"], "/admin/pages/")
        self.assertEqual(captured["path_info"], "/admin/pages/")

class FunctionsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_remove_locked_links_detail(self):
        response = TestClass()
        setattr(response, 'data', {
            'book_faculty_resources': [
                {
                    'link_document_url': 'test',
                    'link_external': 'test',
                    'resource_unlocked': False,
                    'anotherstuff': 'test'
                },
                {
                    'link_document_url': 'test',
                    'link_external': 'test',
                    'resource_unlocked': True,
                    'anotherstuff': 'test'
                }
            ]
        })
        
        remove_locked_links_detail(response)

        self.assertEqual(response.data['book_faculty_resources'][0]["link_document_url"], "")
        self.assertEqual(response.data['book_faculty_resources'][0]["link_external"], "")
        self.assertEqual(response.data['book_faculty_resources'][0]["anotherstuff"], "test")

        self.assertEqual(response.data['book_faculty_resources'][1]["link_document_url"], "test")
        self.assertEqual(response.data['book_faculty_resources'][1]["link_external"], "test")
        self.assertEqual(response.data['book_faculty_resources'][1]["anotherstuff"], "test")

    def test_remove_locked_links_listing(self):
        response = TestClass()
        setattr(response, 'data', {
            'items' : [
                {
                    'book_faculty_resources': [
                        {
                            'link_document_url': 'test',
                            'link_external': 'test',
                            'resource_unlocked': False,
                            'anotherstuff': 'test'
                        },
                        {
                            'link_document_url': 'test',
                            'link_external': 'test',
                            'resource_unlocked': True,
                            'anotherstuff': 'test'
                        }
                    ]
                }
            ]
        })
        
        remove_locked_links_listing(response)

        self.assertEqual(response.data['items'][0]['book_faculty_resources'][0]["link_document_url"], "")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][0]["link_external"], "")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][0]["anotherstuff"], "test")

        self.assertEqual(response.data['items'][0]['book_faculty_resources'][1]["link_document_url"], "test")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][1]["link_external"], "test")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][1]["anotherstuff"], "test")

    def test_build_document_url(self):
        self.assertIn("test/document.pdf", build_document_url("test/test/document.pdf"))

    def test_build_document_url_none(self):
        self.assertEqual(build_document_url(None), None)

    def test_build_image_url_none(self):
        self.assertEqual(build_image_url(None), None)


class TestOpenGraphMiddleware(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='twitterbot')
        self.root_page = Page.objects.get(title="Root")
        self.homepage = RootPage(title="Hello World",
                            slug="openstax-homepage",
                            seo_title='OpenStax Home',
                            search_description='Home page for OpenStax'
                            )
        self.root_page.add_child(instance=self.homepage)

    def test_home_page_link_preview(self):
        response = self.client.get('/')
        self.assertContains(response, 'og:image')


    def test_book_link_preview(self):
        test_image = SimpleUploadedFile(name='openstax.png',
                                        content=open("pages/static/images/openstax.png", 'rb').read())
        self.test_doc = Document.objects.create(title='Test Doc', file=test_image)
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test",
                               )
        # add book index to homepage
        self.homepage.add_child(instance=book_index)
        book = Book(title="Biology 2e",
                    slug="biology-2e",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=self.root_page.locale,
                    license_name='Creative Commons Attribution License',
                    seo_title='Biology 2e',
                    search_description='2nd edition of Biology'
                    )
        book_index.add_child(instance=book)
        self.client = Client(HTTP_USER_AGENT='Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)')
        response = self.client.get('/details/books/biology-2e/')
        self.assertContains(response, 'og:image')

    def test_blog_link_preview(self):
        self.news_index = NewsIndex(title="News Index")
        self.homepage.add_child(instance=self.news_index)
        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                            search_description="Math page description.")
        self.math.save()
        math_id = self.math.id
        self.case_study = BlogContentType(content_type='Case Study')
        self.case_study.save()
        case_study_id = self.case_study.id
        self.learning = BlogCollection(name='Teaching and Learning', description='this is a collection')
        self.learning.save()
        learning_id = self.learning.id
        self.article = NewsArticle(title="Article 1",
                                   slug="article-1",
                                   date=datetime.date.today(),
                                   heading="Sample Article",
                                   subheading="Sample Subheading",
                                   author="OpenStax",
                                   seo_title='Test Article 1',
                                   search_description='Test Article 1 description',
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
                                               {'type': 'item', 'value': {'collection': learning_id, 'featured': False,
                                                                          'popular': False}}]}
                                       ]
                                   ))
        self.news_index.add_child(instance=self.article)
        self.client = Client(HTTP_USER_AGENT='facebookexternalhit/1.1')
        response = self.client.get('/blog/article-1/')
        self.assertContains(response, 'og:image')

    def test_seo_title_used_in_og_tags(self):
        """Test that seo_title is used in Open Graph and Twitter Card tags when available"""
        # Test with middleware (social media bot user agent)
        self.client = Client(HTTP_USER_AGENT='twitterbot')
        response = self.client.get('/')
        # Should use seo_title in og:title meta tag
        self.assertContains(response, 'og:title')
        self.assertContains(response, 'OpenStax Home')
        # Should not contain the page title in OG tags
        self.assertNotContains(response, '<meta property="og:title" content="Hello World"')

    def test_seo_title_used_in_twitter_tags(self):
        """Test that seo_title is used in Twitter Card tags when available"""
        self.client = Client(HTTP_USER_AGENT='Twitterbot/1.0')
        response = self.client.get('/')
        # Should use seo_title in twitter:title meta tag
        self.assertContains(response, 'twitter:title')
        self.assertContains(response, 'OpenStax Home')

    def test_snapshot_canonical_url_has_no_query_string(self):
        """Query-string variants (e.g. utm parameters) declare the clean URL
        as canonical so their signal consolidates onto one page."""
        response = self.client.get('/?utm_source=chatgpt.com&utm_medium=referral')
        self.assertContains(response, 'rel="canonical" href="http://testserver"')
        self.assertContains(response, 'og:url" content="http://testserver"')
        self.assertNotContains(response, 'utm_source')

    def test_k12_flexpage_link_preview(self):
        """K12 subject-group pages are FlexPages (e.g. k12-math), not K12Subjects.
        The middleware should fall back to FlexPage when no K12Subject matches."""
        self.k12_math = FlexPage(title="Math",
                                 slug="k12-math",
                                 seo_title='K12 Math SEO Title',
                                 search_description='K12 Math page description')
        self.homepage.add_child(instance=self.k12_math)
        self.client = Client(HTTP_USER_AGENT='facebookexternalhit/1.1')
        response = self.client.get('/k12/math/')
        self.assertContains(response, 'og:image')
        self.assertContains(response, 'K12 Math SEO Title')

    def test_ai_crawler_gets_og_page(self):
        """AI crawlers (GPTBot etc.) must get the OG snapshot too, not Wagtail's
        404 -- their real UA strings don't always resolve to a stable ua_parser
        family, so the middleware also checks for them by raw substring."""
        self.k12_math = FlexPage(title="Math",
                                 slug="k12-math",
                                 seo_title='K12 Math SEO Title',
                                 search_description='K12 Math page description')
        self.homepage.add_child(instance=self.k12_math)
        self.client = Client(HTTP_USER_AGENT=(
            'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; '
            'GPTBot/1.1; +https://openai.com/gptbot'
        ))
        response = self.client.get('/k12/math/')
        self.assertContains(response, 'og:image')
        self.assertContains(response, 'K12 Math SEO Title')

    def test_claudebot_gets_og_page(self):
        """ClaudeBot (Anthropic's training crawler) resolves to a stable ua_parser
        family and must get the OG page like the other current-generation AI
        crawlers nginx now routes through."""
        self.k12_math = FlexPage(title="Math",
                                 slug="k12-math",
                                 seo_title='K12 Math SEO Title',
                                 search_description='K12 Math page description')
        self.homepage.add_child(instance=self.k12_math)
        self.client = Client(HTTP_USER_AGENT=(
            'Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)'
        ))
        response = self.client.get('/k12/math/')
        self.assertContains(response, 'og:image')
        self.assertContains(response, 'K12 Math SEO Title')

    def test_human_user_agent_does_not_get_og_page(self):
        """A normal browser UA must not be served the bot-only OG snapshot."""
        self.k12_math = FlexPage(title="Math",
                                 slug="k12-math",
                                 seo_title='K12 Math SEO Title',
                                 search_description='K12 Math page description')
        self.homepage.add_child(instance=self.k12_math)
        self.client = Client(HTTP_USER_AGENT=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ))
        response = self.client.get('/k12/math/')
        self.assertNotContains(response, 'K12 Math SEO Title', status_code=404)

    def test_k12_flexpage_serves_real_template_with_jsonld(self):
        """Answer-engine crawlers don't execute JS and can only cite text in the
        raw HTML, so k12 FlexPages serve their full content-bearing template
        with JSON-LD."""
        self.k12_math = FlexPage(title="Math",
                                 slug="k12-math",
                                 seo_title='K12 Math SEO Title',
                                 search_description='K12 Math page description')
        self.homepage.add_child(instance=self.k12_math)
        self.client = Client(HTTP_USER_AGENT='facebookexternalhit/1.1')
        response = self.client.get('/k12/math/')
        self.assertContains(response, 'K12 Math SEO Title')
        self.assertContains(response, 'application/ld+json')
        self.assertContains(response, '"@type": "CollectionPage"')
        self.assertContains(response, 'og:site_name')
        self.assertContains(response, 'og:type" content="website"')
        self.assertContains(response, f'og:url" content="{self.k12_math.get_full_url()}"')
        self.assertContains(response, f'href="{self.k12_math.get_full_url()}"')

    def test_non_flexpage_og_case_still_uses_build_template(self):
        """A non-FlexPage OG match (e.g. book) serves the build_template snapshot;
        the full-template path is FlexPage-only."""
        with open("pages/static/images/openstax.png", 'rb') as image_file:
            image_content = image_file.read()
        test_image = SimpleUploadedFile(name='openstax.png', content=image_content)
        self.test_doc = Document.objects.create(title='Test Doc', file=test_image)
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test",
                               )
        self.homepage.add_child(instance=book_index)
        book = Book(title="Biology 2e",
                    slug="biology-2e-build-template-check",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=self.root_page.locale,
                    license_name='Creative Commons Attribution License',
                    seo_title='Biology 2e',
                    search_description='2nd edition of Biology'
                    )
        book_index.add_child(instance=book)
        self.client = Client(HTTP_USER_AGENT='Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)')
        response = self.client.get('/details/books/biology-2e-build-template-check/')
        self.assertContains(response, 'og:image')
        self.assertContains(response, '<body></body>')
        self.assertNotContains(response, 'application/ld+json')


    # --- Routes osweb serves from the SPA, with no CMS page of their own ---
    # These 404'd to crawlers while returning a working page to every browser,
    # which is why /adoption could never be indexed (CORE-736).

    def _form_headings(self, **overrides):
        fields = dict(
            title='Form Headings',
            slug='form-headings',
            adoption_intro_heading="Let us know you're using OpenStax",
            adoption_intro_description=(
                '<p>Help us keep making free materials by letting us know '
                'you&#x27;ve adopted!</p>'
                '<p>Not using OpenStax yet? Go to our '
                '<a href="/interest">interest form</a>.</p>'
            ),
            interest_intro_heading='Interested in learning more about OpenStax?',
            interest_intro_description=(
                '<p>Fill out the form below and we will send you more '
                'information.</p><p><a href="/adoption">Let us know!</a></p>'
            ),
        )
        fields.update(overrides)
        headings = FormHeadings(**fields)
        self.homepage.add_child(instance=headings)
        return headings

    def _meta_description(self, response):
        match = re.search(
            r'<meta name="description" content="([^"]*)"',
            response.content.decode(),
        )
        self.assertIsNotNone(match, 'snapshot has no meta description')
        return match.group(1)

    def test_adoption_snapshot_comes_from_form_headings(self):
        """/adoption has no page of its own, so its title and description come
        from the FormHeadings adoption_* fields -- which means marketing edits
        what crawlers see in Wagtail, with no redeploy."""
        self._form_headings()
        response = self.client.get('/adoption')
        self.assertContains(response, 'Let us know you&#x27;re using OpenStax')
        self.assertContains(
            response, 'rel="canonical" href="http://testserver/adoption"')

    def test_adoption_snapshot_body_keeps_prose_and_internal_links(self):
        """Answer engines can only cite what's in the raw HTML, so the rich-text
        description is emitted as markup rather than flattened away."""
        self._form_headings()
        response = self.client.get('/adoption')
        self.assertContains(response, 'Help us keep making free materials')
        self.assertContains(response, 'href="/interest"')
        self.assertNotContains(response, '<body></body>')

    def test_interest_snapshot_uses_its_own_fields(self):
        """Both form routes read the same FormHeadings record, so the route has
        to pick the matching field prefix."""
        self._form_headings()
        response = self.client.get('/interest')
        self.assertContains(response, 'Interested in learning more about OpenStax?')
        self.assertContains(response, 'href="/adoption"')
        self.assertNotContains(response, 'Help us keep making free materials')

    def test_form_snapshot_meta_description_is_flattened_text(self):
        """The body keeps its markup but the meta description can't: it needs
        tags stripped, and entities unescaped first so escaping the attribute
        doesn't double-encode them into &amp;#x27;."""
        self._form_headings()
        description = self._meta_description(self.client.get('/adoption'))
        self.assertIn('you&#x27;ve adopted', description)
        self.assertNotIn('&amp;', description)
        self.assertNotIn('&lt;p&gt;', description)

    def test_meta_description_keeps_words_apart_across_blocks(self):
        """strip_tags() only deletes tags, so two paragraphs ran together as
        "adopted!Not using OpenStax yet?" -- a coined word in the one sentence
        search results actually show. Block boundaries become spaces first."""
        self._form_headings()
        description = self._meta_description(self.client.get('/adoption'))
        self.assertIn('adopted! Not using OpenStax yet?', description)
        self.assertNotIn('adopted!Not', description)

    def test_meta_description_does_not_space_out_inline_markup(self):
        """Only block-level tags are boundaries: spacing every tag would put a
        space before the period after a link, and break a word wrapped in
        <em>."""
        self._form_headings(adoption_intro_description=(
            '<p>Read the <a href="/interest">interest form</a>. '
            'It is <em>free</em>.</p>'
        ))
        description = self._meta_description(self.client.get('/adoption'))
        self.assertIn('interest form. It is free.', description)

    def test_form_snapshot_drops_placeholder_tags(self):
        """FormHeadings copy supports {{first_name}} tags that only the frontend
        interpolates. A crawler is never signed in, so any tag reaching the
        snapshot would be published verbatim."""
        self._form_headings(
            adoption_intro_heading='Welcome back, {{first_name}}',
            adoption_intro_description='<p>Your school is {{school}}.</p>',
        )
        response = self.client.get('/adoption')
        self.assertContains(response, 'Welcome back,')
        self.assertNotContains(response, 'first_name')
        self.assertNotContains(response, 'school}}')

    def test_adoption_falls_through_when_form_headings_missing(self):
        """With no FormHeadings record there is nothing to build a snapshot
        from, so the request must fall through rather than serve empty tags.

        sitemap_routes() reads the same record through the same helper, so a
        route in this state isn't advertised either -- see
        global_settings.tests.FrontendOnlyPagesSitemapTest."""
        response = self.client.get('/adoption')
        self.assertEqual(response.status_code, 404)

    def test_unpublished_form_headings_are_not_served(self):
        """The snapshot is rendered straight to the crawler, with none of the
        checks Wagtail's own routing would run. So a record an editor has
        drafted or unpublished must not reach it -- this path would otherwise
        publish unreleased copy to Google on its own."""
        headings = self._form_headings()
        headings.live = False
        headings.save()
        self.assertEqual(self.client.get('/adoption').status_code, 404)

    def test_restricted_form_headings_are_not_served(self):
        """Same for a view restriction: live() doesn't exclude it, and nothing
        downstream of this queryset enforces it."""
        headings = self._form_headings()
        PageViewRestriction.objects.create(
            page=headings, restriction_type=PageViewRestriction.LOGIN)
        self.assertEqual(self.client.get('/adoption').status_code, 404)

    def test_no_copy_means_no_snapshot_for_that_route(self):
        """The gate itself, which the middleware and sitemap_routes() share so
        a route cannot be advertised while 404ing. It answers per route, not
        per record: a route added to FORM_PAGE_ROUTES before its FormHeadings
        fields exist has nothing to render and must stay unserved and
        unadvertised rather than publish an empty title."""
        headings = self._form_headings()
        self.assertTrue(form_route_heading(headings, 'adoption'))
        self.assertEqual(form_route_heading(headings, 'scholarship'), '')
        self.assertEqual(form_route_heading(None, 'adoption'), '')

    def test_browser_user_agent_gets_no_adoption_snapshot(self):
        """The snapshot is crawler-only; browsers keep getting the React form
        from S3, so Django must not answer them here."""
        self._form_headings()
        self.client = Client(HTTP_USER_AGENT=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ))
        response = self.client.get('/adoption')
        self.assertNotContains(response, 'using OpenStax', status_code=404)

    def test_press_resolves_the_news_page(self):
        """osweb serves /press from the CMS page slugged 'news' -- a slug
        mismatch the middleware has to mirror, or /press (plus /newsletter and
        /newsroom, which redirect to it) all dead-end."""
        press = FlexPage(title='Press', slug='news',
                         seo_title='OpenStax Press Room',
                         search_description='News and press resources')
        self.homepage.add_child(instance=press)
        response = self.client.get('/press')
        self.assertContains(response, 'OpenStax Press Room')

    def test_institutional_partnership_application_resolves_its_page(self):
        """osweb serves /institutional-partnership-application from the page
        slugged 'institutional-partnership' -- the second slug mismatch, and
        the one that exercises the generic Page lookup: that page is a
        pages.InstitutionalPartnership, so it gets the meta snapshot rather
        than a FlexPage's full template."""
        partnership = InstitutionalPartnership(
            title='Institutional Partnership Program Application',
            slug='institutional-partnership',
            seo_title='Institutional Partnership Program Application',
            search_description='Apply to the Institutional Partner Program',
            heading_year='2026',
            heading='Institutional Partner Program',
            quote='OpenStax changed our budget.',
            quote_author='A Partner',
        )
        self.homepage.add_child(instance=partnership)
        response = self.client.get('/institutional-partnership-application')
        self.assertContains(response, 'Apply to the Institutional Partner Program')
        # the snapshot's canonical is the requested URL, which is also what
        # this page's get_url_parts now reports (see PAGE_ROUTES_BY_SLUG)
        self.assertContains(
            response,
            'rel="canonical" href="http://testserver/institutional-partnership-application"')

    def test_restricted_page_is_not_served_through_a_slug_mismatch(self):
        """A mismatched slug is served directly rather than through Wagtail's
        routing, so its view restrictions are never checked. public() has to
        exclude the page here or /press hands a restricted page to crawlers."""
        press = FlexPage(title='Press', slug='news',
                         seo_title='OpenStax Press Room',
                         search_description='News and press resources')
        self.homepage.add_child(instance=press)
        PageViewRestriction.objects.create(
            page=press, restriction_type=PageViewRestriction.LOGIN)
        response = self.client.get('/press')
        self.assertNotContains(response, 'OpenStax Press Room', status_code=404)

    def test_unpublished_page_is_not_served_through_a_slug_mismatch(self):
        press = FlexPage(title='Press', slug='news',
                         seo_title='OpenStax Press Room',
                         search_description='News and press resources')
        self.homepage.add_child(instance=press)
        press.live = False
        press.save()
        response = self.client.get('/press')
        self.assertNotContains(response, 'OpenStax Press Room', status_code=404)

    def test_edtech_partner_program_resolves_its_general_page(self):
        """The entry reading osweb's router turned up: /edtech-partner-program
        is in its mismatch map, serves 200 in a browser, and 404'd to crawlers.
        The page is a GeneralPage under a much longer slug."""
        partner_program = GeneralPage(
            title='OpenStax Technology Partner Program',
            slug='openstax-ally-technology-partner-program',
            seo_title='OpenStax Technology Partner Program',
            search_description='Partner with OpenStax on educational technology',
        )
        self.homepage.add_child(instance=partner_program)
        response = self.client.get('/edtech-partner-program')
        self.assertContains(
            response, 'Partner with OpenStax on educational technology')

    def test_alias_snapshot_is_canonical_to_the_real_page(self):
        """/openstax-ally-technology-partner-program is the canonical page, and
        it serves crawlers too. So the snapshot on the alias has to point at
        it: two URLs each claiming to be canonical compete with each other."""
        # the page has to sit in the site tree for it to have a URL at all,
        # which in production it does
        site = Site.objects.filter(is_default_site=True).first()
        site.root_page = self.homepage
        site.save()
        partner_program = GeneralPage(
            title='OpenStax Technology Partner Program',
            slug='openstax-ally-technology-partner-program',
            search_description='Partner with OpenStax on educational technology',
        )
        self.homepage.add_child(instance=partner_program)

        response = self.client.get('/edtech-partner-program')
        self.assertContains(
            response,
            'rel="canonical" href="http://testserver/openstax-ally-technology-'
            'partner-program"')
        self.assertNotContains(
            response, 'href="http://testserver/edtech-partner-program"')

    def test_mismatch_target_requested_directly_still_redirects(self):
        """/news and /institutional-partnership are 301s in production (to
        /blog and /higher-education). Matching on the target slug alone let a
        crawler requesting them directly be answered here, which
        short-circuits RedirectMiddleware -- so a page that had deliberately
        been moved served a 200 snapshot competing with the URL it moved to."""
        press = FlexPage(title='Press', slug='news',
                         seo_title='OpenStax Press Room',
                         search_description='News and press resources')
        self.homepage.add_child(instance=press)
        Redirect.add_redirect('/news', '/blog')

        response = self.client.get('/news')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/blog')

    def test_mismatch_target_without_a_redirect_is_left_to_wagtail(self):
        """Without a redirect entry the request simply falls through, rather
        than being answered from the mismatch branch."""
        press = FlexPage(title='Press', slug='news',
                         seo_title='OpenStax Press Room',
                         search_description='News and press resources')
        self.homepage.add_child(instance=press)
        response = self.client.get('/news')
        self.assertNotContains(response, 'OpenStax Press Room', status_code=404)

    def test_blog_post_slug_is_not_remapped_by_slug_mismatch(self):
        """Slug remapping applies to whole top-level paths only: a post slugged
        'press' must stay itself rather than resolving to the press page."""
        press = FlexPage(title='Press', slug='news',
                         seo_title='OpenStax Press Room',
                         search_description='News and press resources')
        self.homepage.add_child(instance=press)
        response = self.client.get('/blog/press')
        self.assertNotContains(response, 'OpenStax Press Room', status_code=404)

    def test_blog_index_resolves_to_news_index(self):
        """The index, not a post. url_path is stripped of its trailing slash
        before the '/blog/' test, so /blog matched nothing and 404'd even though
        sitemap.xml advertises it."""
        blog = NewsIndex(title='Blog', slug='openstax-news',
                         seo_title='OpenStax Blog',
                         search_description='OpenStax news and updates')
        self.homepage.add_child(instance=blog)
        response = self.client.get('/blog')
        self.assertContains(response, 'OpenStax Blog')

    def test_unpublished_blog_index_is_not_served(self):
        """The caller serves whatever this lookup returns first, so .all()
        would hand over a draft index."""
        blog = NewsIndex(title='Blog', slug='openstax-news',
                         seo_title='OpenStax Blog',
                         search_description='OpenStax news and updates')
        self.homepage.add_child(instance=blog)
        blog.live = False
        blog.save()
        response = self.client.get('/blog')
        self.assertNotContains(response, 'OpenStax Blog', status_code=404)

    def test_blog_index_resolves_the_default_locale_index(self):
        """There is an index per locale, and .all() picked by insertion order.
        /blog is the English route, so it has to name the locale."""
        spanish = Locale.objects.create(language_code='es')
        es_blog = NewsIndex(title='Blog es', slug='openstax-news-es',
                            seo_title='OpenStax Blog es',
                            search_description='Noticias de OpenStax',
                            locale=spanish)
        self.homepage.add_child(instance=es_blog)
        en_blog = NewsIndex(title='Blog', slug='openstax-news',
                            seo_title='OpenStax Blog',
                            search_description='OpenStax news and updates')
        self.homepage.add_child(instance=en_blog)
        response = self.client.get('/blog')
        self.assertContains(response, 'OpenStax Blog')
        self.assertNotContains(response, 'Noticias de OpenStax')

    def test_separatemap_snapshot_describes_the_map(self):
        """The map page does describe itself -- but in JavaScript, via
        useDocumentHead(), where a crawler never sees it. The snapshot serves
        the same strings, plus the sentence that introduces the map on /about,
        since the page itself is an interactive map with no prose to read."""
        response = self.client.get('/separatemap')
        self.assertContains(response, '<title>Institution Map - OpenStax</title>')
        self.assertContains(response, 'Searchable map of institutions')
        self.assertContains(response, 'more than 160 countries')
        self.assertContains(
            response, 'rel="canonical" href="http://testserver/separatemap"')

    def test_adopters_snapshot_carries_no_adopter_records(self):
        """/adopters renders 11,000+ institutions from /apps/cms/api/adopters/,
        whose description field is unpublished CRM free text the page itself
        never shows. Serving that to crawlers only would leak internal notes and
        be cloaking, so the snapshot is title and description with no body."""
        Adopter.objects.create(
            sales_id='001',
            name='Centre College',
            description='use moodle for course management system at univ.',
            website='http://www.centre.edu/',
        )
        response = self.client.get('/adopters')
        self.assertContains(
            response, 'Complete list of institutions that have adopted OpenStax')
        self.assertNotContains(response, 'Centre College')
        self.assertNotContains(response, 'use moodle')
        self.assertContains(response, '<body></body>')
