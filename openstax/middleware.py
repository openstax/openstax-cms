from django.http import HttpResponsePermanentRedirect
from django.core.handlers.base import BaseHandler
from django.middleware.common import CommonMiddleware
from django.conf import settings
from ua_parser import user_agent_parser
from wagtail.models import Page
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from books.models import Book
from openstax.functions import build_image_url
from news.models import NewsArticle
from pages.models import HomePage, Supporters


class HttpSmartRedirectResponse(HttpResponsePermanentRedirect):
    pass


class CommonMiddlewareAppendSlashWithoutRedirect(CommonMiddleware):
    """ This class converts HttpSmartRedirectResponse to the common response
        of Django view, without redirect.
    """
    response_redirect_class = HttpSmartRedirectResponse

    def __init__(self, *args, **kwargs):
        # create django request resolver
        self.handler = BaseHandler()

        # prevent recursive includes
        old = settings.MIDDLEWARE
        name = self.__module__ + '.' + self.__class__.__name__
        settings.MIDDLEWARE = [i for i in settings.MIDDLEWARE if i != name]

        self.handler.load_middleware()

        settings.MIDDLEWARE = old
        super(CommonMiddlewareAppendSlashWithoutRedirect, self).__init__(*args, **kwargs)

    def process_response(self, request, response):
        response = super(CommonMiddlewareAppendSlashWithoutRedirect, self).process_response(request, response)

        if isinstance(response, HttpSmartRedirectResponse):
            if not request.path.endswith('/'):
                request.path = request.path + '/'
            # we don't need query string in path_info because it's in request.GET already
            request.path_info = request.path
            response = self.handler.get_response(request)

        return response


class CommonMiddlewareOpenGraphRedirect(CommonMiddleware):
    OG_USER_AGENTS = [
        'twitterbot',
        'facebookbot',
        'pinterestbot',
        'slackbot-linkexpanding',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if 'HTTP_USER_AGENT' in request.META:

            user_agent = user_agent_parser.ParseUserAgent(request.META["HTTP_USER_AGENT"])
            if user_agent['family'].lower() in self.OG_USER_AGENTS:
                # url path minus the trailing /
                url_path = request.get_full_path()[:-1]

                full_url = request.build_absolute_uri()

                # imdex of last / to find slug, except when there isn't a last /
                if url_path == '':
                    page_slug = "openstax-homepage"
                else:
                    index = url_path.rindex('/')
                    page_slug = url_path[index+1:]

                if self.redirect_path_found(url_path):
                    # supporters page has the wrong slug
                    if page_slug == 'foundation':
                        page_slug = 'supporters'

                    # look up correct object based on path
                    if '/details/books/' in url_path:
                        page = Book.objects.filter(slug = page_slug)
                    elif '/blog/' in url_path:
                        page = NewsArticle.objects.filter(slug = page_slug)
                    else:
                        page = self.page_by_slug(page_slug)

                    template = self.build_template(page[0], full_url)
                    return HttpResponse(template)
                else:
                    return self.get_response(request)
        return self.get_response(request)

    def build_template(self, page, page_url):
        image_url = self.image_url(page.promote_image)
        template = '<!DOCTYPE html> <html> <head> <meta charset="utf-8">'
        template += '<title>' + str(page.seo_title) + '</title>'
        template += '<meta name = "description" content = "{}" >'.format(page.search_description)
        template += '<link rel = "canonical" href = "{}" />'.format(page_url)
        template += '<meta name = "og:url" content = "{}" >'.format(page_url)
        template += '<meta property="og:type" content="article" />'
        template += '<meta name = "og:title" content = "{}" >'.format(page.seo_title)
        template += '<meta name = "og:description" content = "{}" >'.format(page.search_description)
        template += '<meta name = "og:image" content = "{}" >'.format(image_url)
        template += '<meta name = "og:image:alt" content = "{}" >'.format(page.seo_title)
        template += '<meta name = "twitter:card" content = "summary_large_image" >'
        template += '<meta name = "twitter:site" content = "@OpenStax" >'
        template += '<meta name = "twitter:title"content = "{}" >'.format(page.seo_title)
        template += '<meta name = "twitter:description" content = "{}" >'.format(page.search_description)
        template += '< meta name = "twitter:image" content = "{}" >'.format(image_url)
        template += '<meta name = "twitter:image:alt"content = "OpenStax" >'

        template += '</head><body></body></html>'
        return template

    def redirect_path_found(self, url_path):
        if '/blog/' in url_path or '/details/books/' in url_path or '/foundation' in url_path or '' == url_path:
            return True
        else:
            return False

    def image_url(self, image):
        image_url = build_image_url(image)
        if not image_url:
            return ''
        return image_url

    def page_by_slug(self, page_slug):
        if page_slug == 'supporters':
            return Supporters.objects.all()
        if page_slug == 'openstax-homepage':
            return HomePage.objects.filter(locale = 1)




