from time import time

from django.http import HttpResponsePermanentRedirect
from django.core.handlers.base import BaseHandler
from django.middleware.common import CommonMiddleware
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from wagtail.contrib.redirects import middleware, models
from django import http
import requests
from urllib.parse import urlparse


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


class RedirectMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        print('**[process_response] called')
        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        # Get the path
        path = models.Redirect.normalise_path(request.get_full_path())
        print('***path: ' + path)

        # Find redirect
        redirect = middleware.get_redirect(request, path)
        if redirect is None:
            # Get the path without the query string or params
            path_without_query = urlparse(path).path

            if path == path_without_query:
                # don't try again if we know we will get the same response
                return response

            redirect = middleware.get_redirect(request, path_without_query)
            if redirect is None:
                return response

        if redirect.link is None:
            return response

        if redirect.is_permanent:
            self.send_google_analytics(request.get_host(),path)
            return http.HttpResponsePermanentRedirect(redirect.link)
        else:
            self.send_google_analytics(request.get_host(),path)
            return http.HttpResponseRedirect(redirect.link)

    def send_google_analytics(self, host, path):
        escaped_url = requests.utils.quote('https://' + host + path)
        print('**[send_google_analytics] called: ' + escaped_url)
        payload = {'v':'1', #api version
                   't':'event', #hit type
                   'cid':str(int(time() * 1000)), #client id (sending timestamp since we have no user)
                   'tid':settings.GOOGLE_ANALYTICS['code'], #Google Analytics id
                   'ec':'Redirect', #event category
                   'ea':'open', #event action
                   'el':path #event label - short code
                   }

        print('**[send_google_analytics] payload: ' + str(payload))
        response = requests.post(
            url='https://www.google-analytics.com/collect',
            params=payload,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}
        )
        print('**[send_google_analytics] response: ' + str(response.status_code))
