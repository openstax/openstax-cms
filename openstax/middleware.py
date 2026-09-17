import re

from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.core.handlers.base import BaseHandler
from django.middleware.common import CommonMiddleware
from django.utils.html import escape, strip_tags
from django.utils.http import escape_leading_slashes
from django.utils.text import Truncator
from django.conf import settings

from ua_parser import user_agent_parser
from html import unescape
from urllib.parse import unquote
from wagtail.models import Locale, Page
from wagtail.rich_text import expand_db_html

from api.models import FeatureFlag
from books.models import Book, BookIndex
from openstax.frontend_routes import FORM_PAGE_ROUTES, SLUG_MISMATCHES, STATIC_PAGES
from openstax.functions import build_image_url
from news.models import NewsArticle, NewsIndex
from pages.models import (
    Supporters, PrivacyPolicy, K12Subject, Subject, Subjects, RootPage, FlexPage,
    FormHeadings,
)


class CommonMiddlewareAppendSlashWithoutRedirect(CommonMiddleware):
    """ This class converts HttpResponsePermanentRedirect to the common response
        of Django view, without redirect. This is necessary to match status_codes
        for urls like /url?q=1 and /url/?q=1. If you don't use it, you will have 302
        code always on pages without slash.
    """
    response_redirect_class = HttpResponsePermanentRedirect

    def __init__(self, *args, **kwargs):
        # create django request resolver
        self.handler = BaseHandler()

        # prevent recursive includes
        old = settings.MIDDLEWARE
        name = self.__module__ + '.' + self.__class__.__name__
        settings.MIDDLEWARE = [i for i in settings.MIDDLEWARE if i != name]

        self.handler.load_middleware()

        settings.MIDDLEWARE = old
        super().__init__(*args, **kwargs)

    def get_full_path_with_slash(self, request):
        """ Return the full path of the request with a trailing slash appended
            without Exception in Debug mode
        """
        # Prevent construction of scheme relative urls.
        new_path = request.get_full_path(force_append_slash=True)
        new_path = escape_leading_slashes(new_path)
        return new_path

    def process_response(self, request, response):
        response = super().process_response(request, response)

        if isinstance(response, HttpResponsePermanentRedirect):
            # Append the trailing slash and re-dispatch internally instead of
            # redirecting. Django's URL resolver matches on request.path_info,
            # so it must get the slash too: updating only request.path leaves the
            # re-dispatch resolving the original slash-less path, which 404s.
            # (The query string stays in request.GET, so path_info needs none.)
            if not request.path.endswith('/'):
                request.path = request.path + '/'
            if not request.path_info.endswith('/'):
                request.path_info = request.path_info + '/'
            response = self.handler.get_response(request)

        return response


class CommonMiddlewareOpenGraphRedirect(CommonMiddleware):
    OG_USER_AGENTS = {
        'baiduspider', 'bingbot', 'embedly', 'facebookbot', 'facebookexternalhit/1.1',
        'facebookexternalhit', 'facebot', 'google.*snippet', 'googlebot', 'linkedinbot',
        'metadatascraper', 'outbrain', 'pinterest', 'pinterestbot', 'quora', 'quora link preview',
        'rogerbot', 'showyoubot', 'slackbot', 'slackbot-linkexpanding', 'twitterbot', 'vkshare',
        'w3c_validator', 'whatsapp', 'yandex', 'yahoo',
        'gptbot', 'perplexitybot', 'applebot',
        'oai-searchbot', 'claudebot', 'claude-searchbot',
    }

    # ua_parser doesn't resolve these AI crawlers to a stable family
    # (e.g. ChatGPT-User parses as family "com/bot"), so they're matched
    # as raw substrings, mirroring the nginx user-agent map.
    AI_CRAWLER_USER_AGENT_SUBSTRINGS = (
        'chatgpt-user', 'google-extended', 'anthropic-ai', 'claude-web',
        'claude-user', 'perplexity-user',
    )

    # FormHeadings copy supports these tags, which only the frontend
    # interpolates (from the signed-in user's profile).
    PLACEHOLDER_TAG = re.compile(r'\{\{\w+\}\}')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if 'HTTP_USER_AGENT' in request.META:
            raw_user_agent = request.META['HTTP_USER_AGENT']
            user_agent = user_agent_parser.ParseUserAgent(raw_user_agent)
            is_og_user_agent = user_agent['family'].lower() in self.OG_USER_AGENTS or any(
                substring in raw_user_agent.lower() for substring in self.AI_CRAWLER_USER_AGENT_SUBSTRINGS
            )
            if is_og_user_agent:
                url_path = unquote(request.path_info.rstrip('/'))
                full_url = unquote(request.build_absolute_uri())
                page_slug = "home" if url_path == '' else url_path.rsplit('/', 1)[-1]

                if self.redirect_path_found(url_path):
                    route = url_path.lstrip('/')

                    # Routes osweb serves from the SPA with no CMS page of
                    # their own -- see openstax.frontend_routes.
                    response = self.frontend_only_response(route, full_url)
                    if response:
                        return response

                    # A top-level osweb URL can differ from the slug of the CMS
                    # page it renders. Only remap a whole path: a blog post
                    # slugged 'press' must not resolve to the press page.
                    if route == page_slug:
                        page_slug = SLUG_MISMATCHES.get(page_slug, page_slug)

                    page = self.get_page(url_path, page_slug)
                    if page:
                        instance = page[0]
                        # answer-engine crawlers don't execute JS and can only cite
                        # what's in the raw HTML, so FlexPages serve their full
                        # content-bearing template
                        if isinstance(instance, FlexPage):
                            return instance.serve(request).render()
                        template = self.build_template(instance, full_url)
                        return HttpResponse(template)
        return self.get_response(request)

    def get_page(self, url_path, page_slug):
        if '/details/books/' in url_path:
            return Book.objects.filter(slug=page_slug)
        elif url_path == '/blog':
            # The blog index, not a post. url_path has already had its trailing
            # slash stripped, so the '/blog/' test below can never match it --
            # which left the index 404ing even though sitemap.xml advertises it.
            return NewsIndex.objects.all()
        elif '/blog/' in url_path:
            return NewsArticle.objects.filter(slug=page_slug)
        elif '/privacy' in url_path:
            return PrivacyPolicy.objects.filter(slug='privacy-policy')
        elif '/k12' in url_path:
            return (K12Subject.objects.filter(slug='k12-' + page_slug)
                    or FlexPage.objects.filter(slug='k12-' + page_slug))
        elif '/subjects' in url_path:
            flag = FeatureFlag.objects.filter(name='new_subjects')
            if flag[0].feature_active:
                if page_slug == 'subjects':
                    page_slug = 'new-subjects'
                    return Subjects.objects.filter(slug=page_slug)
                else:
                    return Subject.objects.filter(slug=page_slug + '-books')
            else:
                return BookIndex.objects.filter(slug='subjects')
        else:
            return self.page_by_slug(page_slug)

    def frontend_only_response(self, route, full_url):
        """ Crawler snapshot for a route osweb serves from the SPA with no CMS
            page of its own. Returns None if `route` isn't one of them, so the
            caller falls through to the normal page lookup.
        """
        if route in FORM_PAGE_ROUTES:
            headings = self.form_headings()
            if headings is None:
                return None
            return HttpResponse(self.build_form_page_template(headings, route, full_url))

        if route in STATIC_PAGES:
            title, description = STATIC_PAGES[route]
            return HttpResponse(self.build_snapshot(title, description, full_url))

        return None

    def form_headings(self):
        """ The FormHeadings record holding the adoption and interest copy.

            max_count = 1 is per-locale (there is an en record and an es one),
            so this pins the default locale rather than assuming a single row.
        """
        return FormHeadings.objects.filter(locale=Locale.get_default()).first()

    def build_form_page_template(self, headings, route, full_url):
        # Always the logged-out fields: a crawler is never signed in, and the
        # logged-in variants are the ones that carry {{first_name}} tags.
        heading = self.strip_placeholders(
            getattr(headings, '{}_intro_heading'.format(route), '') or ''
        )
        description_html = self.strip_placeholders(expand_db_html(
            getattr(headings, '{}_intro_description'.format(route), '') or ''
        ))

        return self.build_snapshot(
            heading,
            self.meta_description(description_html),
            full_url,
            # emitted as markup, not text, so answer engines get real prose and
            # the internal /adoption <-> /interest links survive as anchors
            body=description_html,
            image_url=self.image_url(headings.promote_image),
        )

    @classmethod
    def strip_placeholders(cls, text):
        """ Drop any {{tag}} the frontend would have interpolated. Nothing
            interpolates them here, so one left in place would be published
            verbatim to a crawler.
        """
        return cls.PLACEHOLDER_TAG.sub('', text)

    @staticmethod
    def meta_description(rich_text, limit=155):
        """ Flatten rich text into a meta description.

            strip_tags leaves entities alone (&#x27;), so they're unescaped here
            to stop build_snapshot's escape() double-encoding them into
            &amp;#x27;. Plain CharField copy must not go through this.
        """
        text = ' '.join(unescape(strip_tags(rich_text)).split())
        return Truncator(text).chars(limit)

    def build_snapshot(self, title, description, full_url, body='', image_url=''):
        """ Snapshot for a route with no CMS page to hand to build_template.

            Everything landing in an attribute is escaped. `body` is trusted
            CMS rich text and is emitted as markup on purpose.
        """
        # canonical and og:url point at the clean URL so query-string
        # variants consolidate their signal onto one page
        page_url = escape(full_url.split('?', 1)[0].rstrip('/'))
        title = escape(title)
        description = escape(description)
        image_url = escape(image_url)
        return f'''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{title}</title>
                <meta name="description" content="{description}">
                <link rel="canonical" href="{page_url}">
                <meta property="og:url" content="{page_url}">
                <meta property="og:type" content="website">
                <meta property="og:site_name" content="OpenStax">
                <meta property="og:title" content="{title}">
                <meta property="og:description" content="{description}">
                <meta property="og:image" content="{image_url}">
                <meta property="og:image:alt" content="OpenStax: {title}">
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:site" content="@OpenStax">
                <meta name="twitter:title" content="{title}">
                <meta name="twitter:description" content="{description}">
                <meta name="twitter:image" content="{image_url}">
                <meta name="twitter:image:alt" content="OpenStax">
            </head>
            <body>{body}</body>
            </html>'''

    def build_template(self, page, page_url):
        # canonical and og:url point at the clean URL so query-string
        # variants consolidate their signal onto one page
        page_url = page_url.split('?', 1)[0].rstrip('/')
        image_url = self.image_url(page.promote_image)
        # Use seo_title if available, otherwise fall back to title
        display_title = page.seo_title if page.seo_title else page.title
        return f'''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{page.title}</title>
                <meta name="description" content="{page.search_description}">
                <link rel="canonical" href="{page_url}">
                <meta property="og:url" content="{page_url}">
                <meta property="og:type" content="article">
                <meta property="og:title" content="{display_title}">
                <meta property="og:description" content="{page.search_description}">
                <meta property="og:image" content="{image_url}">
                <meta property="og:image:alt" content="OpenStax: {display_title}">
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:site" content="@OpenStax">
                <meta name="twitter:title" content="{display_title}">
                <meta name="twitter:description" content="{page.search_description}">
                <meta name="twitter:image" content="{image_url}">
                <meta name="twitter:image:alt" content="OpenStax">
            </head>
            <body></body>
            </html>'''

    def redirect_path_found(self, url_path):
        return any(substring in url_path for substring in ['/blog/', '/details/books/', '/foundation', '/privacy', '/subjects', '']) or '/k12' in url_path

    def image_url(self, image):
        return build_image_url(image) or ''

    def page_by_slug(self, page_slug):
        if page_slug == 'supporters':
            return Supporters.objects.all()
        if page_slug == 'home':
            return RootPage.objects.filter(locale=1)
        # Reachable only via SLUG_MISMATCHES, where the osweb URL differs from
        # where the page sits in the tree -- so Wagtail's own routing can't
        # serve it and falling through would 404. Restricted to mapped slugs on
        # purpose: every other path keeps falling through to Wagtail, which
        # serves the page's full template rather than a bare meta snapshot.
        if page_slug in SLUG_MISMATCHES.values():
            return Page.objects.live().filter(
                slug=page_slug, locale=Locale.get_default()
            ).specific()
