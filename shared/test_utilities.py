from django.urls import resolve, Resolver404
from django.core.handlers.base import BaseHandler
from django.test.client import RequestFactory
from django.http.response import HttpResponsePermanentRedirect
from django.contrib.auth.models import User


def assertPathDoesNotRedirectToTrailingSlash(test, path):
    try:
        resolve(path)
    except Resolver404:
        test.fail('The path {} cannot be found'.format(path))

    response = test.client.get(path)

    if isinstance(response, HttpResponsePermanentRedirect):
        test.assertNotEqual(response.url, path + "/")


def mock_user_login():
    user, _ = User.objects.get_or_create(
        username='test',
        first_name='Test',
        last_name='User',
        email='test@openstax.org'
    )

    return user


class RequestMock(RequestFactory):
    def request(self, **request):
        """Construct a generic request object."""
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request mock object - request middleware returned a response")
        return request
