from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.core.handlers.base import BaseHandler
from django.middleware.common import CommonMiddleware
from django.utils.http import escape_leading_slashes
from django.conf import settings

from ua_parser import user_agent_parser
from urllib.parse import unquote

from api.models import FeatureFlag
from books.models import Book, BookIndex
from openstax.functions import build_image_url
from news.models import NewsArticle
from pages.models import HomePage, Supporters, PrivacyPolicy, K12Subject, Subject, Subjects, RootPage


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
            if not request.path.endswith('/'):
                request.path = request.path + '/'
            # we don't need query string in path_info because it's in request.GET already
            response = self.handler.get_response(request)

        return response


class CommonMiddlewareOpenGraphRedirect(CommonMiddleware):
    OG_USER_AGENTS = {
        'baiduspider', 'bingbot', 'embedly', 'facebookbot', 'facebookexternalhit/1.1',
        'facebookexternalhit', 'facebot', 'google.*snippet', 'googlebot', 'linkedinbot',
        'MetadataScraper', 'outbrain', 'pinterest', 'pinterestbot', 'quora', 'quora link preview',
        'rogerbot', 'showyoubot', 'slackbot', 'slackbot-linkexpanding', 'twitterbot', 'vkShare',
        'W3C_Validator', 'WhatsApp', 'yandex', 'yahoo'
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if 'HTTP_USER_AGENT' in request.META:
            user_agent = user_agent_parser.ParseUserAgent(request.META["HTTP_USER_AGENT"])
            if user_agent['family'].lower() in self.OG_USER_AGENTS:
                url_path = unquote(request.get_full_path()[:-1])
                full_url = unquote(request.build_absolute_uri())
                page_slug = "home" if url_path == '' else url_path.rsplit('/', 1)[-1]

                if self.redirect_path_found(url_path):
                    if page_slug == 'foundation':
                        page_slug = 'supporters'

                    page = self.get_page(url_path, page_slug)
                    if page:
                        template = self.build_template(page[0], full_url)
                        return HttpResponse(template)
        return self.get_response(request)

    def get_page(self, url_path, page_slug):
        if '/details/books/' in url_path:
            return Book.objects.filter(slug=page_slug)
        elif '/blog/' in url_path:
            return NewsArticle.objects.filter(slug=page_slug)
        elif '/privacy' in url_path:
            return PrivacyPolicy.objects.filter(slug='privacy-policy')
        elif '/k12' in url_path:
            return K12Subject.objects.filter(slug='k12-' + page_slug)
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

    def build_template(self, page, page_url):
        page_url = page_url.rstrip('/')
        image_url = self.image_url(page.promote_image)
        return f'''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{page.title}</title>
                <meta name="description" content="{page.search_description}">
                <link rel="canonical" href="{page_url}">
                <meta property="og:url" content="{page_url}">
                <meta property="og:type" content="article">
                <meta property="og:title" content="{page.title}">
                <meta property="og:description" content="{page.search_description}">
                <meta property="og:image" content="{image_url}">
                <meta property="og:image:alt" content="{page.title}">
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:site" content="@OpenStax">
                <meta name="twitter:title" content="{page.title}">
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
        if page_slug == 'openstax-homepage':
            return HomePage.objects.filter(locale=1)
        if page_slug == 'home':
            return RootPage.objects.filter(locale=1)