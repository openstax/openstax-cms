# -*- coding: utf-8 -*-

from requests.exceptions import ConnectionError


class EventbriteException(Exception):
    pass


class IllegalHttpMethod(EventbriteException):
    pass


class InvalidResourcePath(EventbriteException):
    pass


class UnknownEndpoint(EventbriteException):
    pass


class UnsupportedEndpoint(EventbriteException):
    pass


class InternetConnectionError(ConnectionError):
    """
    Wraps requests.exceptions.ConnectionError in order to provide a more
    intuitively named exception.
    """
    pass


class InvalidWebhook(EventbriteException):
    pass
