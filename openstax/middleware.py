from django.http import HttpResponsePermanentRedirect
from django.core.handlers.base import BaseHandler
from django.middleware.common import CommonMiddleware
from django.conf import settings
from ua_parser import user_agent_parser
from wagtail.models import Page
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse


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
        'facebookexternalhit',
        'pinterest',
        'slackbot-linkexpanding',
    ]
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        user_agent = user_agent_parser.ParseUserAgent(request.META["HTTP_USER_AGENT"])
        if user_agent['family'].lower() in self.OG_USER_AGENTS:
            url_path = request.get_full_path()[:-1]
            full_url = request.build_absolute_uri()
            index = url_path.rindex('/')
            page_slug = url_path[index+1:]
            if '/blog/' in url_path or '/details/books/' in url_path:
                page = Page.objects.filter(slug = page_slug)
                template = self.build_template(page[0], full_url)
                return HttpResponse(template)
            else:
                return self.get_response(request)

        else:
            return self.get_response(request)

    def build_template(self, page, page_url):
        template = '<!DOCTYPE html> <html> <head> <meta charset="utf-8">'
        template += '<title>' + str(page.seo_title) + '</title>'
        template += '<meta name = "description" content = "{}" >'.format(page.search_description)
        template += '<link rel = "canonical" href = "{}" />'.format(page_url)
        template += '<meta name = "og:url" content = "{}" >'.format(page_url)
        template += '<meta property="og:type" content="article" />'
        template += '<meta name = "og:title" content = "{}" >'.format(page.seo_title)
        template += '<meta name = "og:description" content = "{}" >'.format(page.search_description)
        template += '<meta name = "og:image" content = "{}" >'.format(page.promote_image.url)
        template += '<meta name = "og:image:alt" content = "{}" >'.format(page.seo_title)
        template += '<meta name = "twitter:card" content = "summary_large_image" >'
        template += '<meta name = "twitter:site" content = "@OpenStax" >'
        template += '<meta name = "twitter:title"content = "{}" >'.format(page.seo_title)
        template += '<meta name = "twitter:description" content = "{}" >'.format(page.search_description)
        template += '< meta name = "twitter:image" content = "{}" >'.format(page.promote_image.url)
        template += '<meta name = "twitter:image:alt"content = "OpenStax" >'

        template += '</head><body></body></html>'
        print(str(template))
        return template

