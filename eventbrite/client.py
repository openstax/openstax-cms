# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from platform import platform

import requests

from .access_methods import AccessMethodsMixin
from .compat import json, string_type
from .decorators import objectify
from .exceptions import (
    IllegalHttpMethod,
    InvalidWebhook
)
from . import __version__
from .utils import (
    format_path,
    construct_namespaced_dict,
    get_webhook_from_request,
    EVENTBRITE_API_URL
)


class Eventbrite(AccessMethodsMixin):

    allowed_methods = ['post', 'get', 'delete']
    content_type_specified = True

    def __init__(self, oauth_token, eventbrite_api_url=EVENTBRITE_API_URL):
        self.oauth_token = oauth_token
        self.eventbrite_api_url = eventbrite_api_url

    @property
    def headers(self):
        headers = {
            "content-type": "application/json",
            "Authorization": "Bearer {0}".format(self.oauth_token),
            "User-Agent": "eventbrite-python-sdk {version} ({system})".format(
                version=__version__,
                system=platform(),
            )
        }
        return headers

    def api(self, method, path, data, expand=()):
        method = method.strip().lower()
        if method not in self.allowed_methods:
            msg = "The '{0}' method is not accepted by the Eventbrite " \
                "client.".format(method)
            raise IllegalHttpMethod(msg)
        method = getattr(self, method)
        return method(path, data)

    @objectify
    def get(self, path, data=None, expand=()):
        # Resolves the search result response problem
        headers = self.headers
        if 'content-type' in headers:
            headers.pop('content-type')
        # Get the function path
        path = format_path(path, self.eventbrite_api_url)

        if data is None:
            data = {}

        # Manage expansions
        if data.get('expand'):
            # Do nothing because expand is already passed in
            pass
        elif expand:
            # Manage expansions
            data['expand'] = ','.join(expand)
        else:
            # Anything else is None
            data['expand'] = 'none'
        return requests.get(path, headers=headers, params=data or {})

    @objectify
    def post(self, path, data=None):
        path = format_path(path, self.eventbrite_api_url)
        json_data = json.dumps(data or {})
        return requests.post(path, headers=self.headers, data=json_data)

    @objectify
    def delete(self, path, data=None):
        path = format_path(path, self.eventbrite_api_url)
        return requests.delete(path, headers=self.headers, data=data or {})

    ############################
    #
    # Access methods
    #
    ############################

    def get_user(self, user_id=None):
        """
        Returns a user for the specified user as user.

        GET users/:id/

        :param int user_id: (optional) The id assigned to a user

        """
        if user_id:
            return self.get('/users/{0}/'.format(user_id))
        return self.get('/users/me/')

    def get_user_orders(self, user_id=None, changed_since=None):
        """
        Returns a paginated response of orders, under the key orders, of all
        orders the user has placed (i.e. where the user was the person buying
        the tickets).

        GET users/:id/orders/

        :param int user_id: (optional) The id assigned to a user. Leave empty
            to get current user.
        :param datetime changed_since: (optional) Only return attendees changed
            on or after the time given

        .. note:: A datetime represented as a string in ISO8601 combined date
            and time format, always in UTC.
        """
        if user_id:
            url = '/users/{0}/orders/'.format(user_id)
        else:
            url = '/users/me/orders/'

        data = {}
        if changed_since:
            data['changed_since'] = changed_since
        return self.get(url, data=data)

    def get_event_attendees(self, event_id, status=None, changed_since=None, page=1):
        """
        Returns a paginated response with a key of attendees, containing a
        list of attendee.

        GET /events/:id/attendees/

        :param status: (optional)
        :param datetime changed_since: (optional) Only return attendees changed
            on or after the time given
        :param int page: (optional) Since the response is paginated then this
            allows you to specify which page to fetch.
        .. note:: A datetime represented as a string in ISO8601 combined date
            and time format, always in UTC.
        """
        data = {}
        if status:  # TODO - check the types of valid status
            data['status'] = status
        if changed_since:
            data['changed_since'] = changed_since
        if page:
            data['page'] = page
        return self.get("/events/{0}/attendees/".format(event_id), data=data)

    def get_event_attendee_by_id(self, event_id, attendee_id):
        """
        GET /events/:id/attendees/:id/
        """
        return self.get("/events/{0}/attendees/{1}/".format(event_id, attendee_id))

    def get_event_ticket_classes(self, event_id):
        """
        Returns a paginated response with a key of ticket_classes, containing
        a list of ticket_class.

        GET /events/:id/ticket_classes/
        """
        return self.get("/events/{0}/ticket_classes/".format(event_id))

    def get_event_ticket_class_by_id(self, event_id, ticket_class_id):
        """
        GET /events/:id/ticket_classes/:id/
        """
        return self.get("/events/{0}/ticket_classes/{1}/".format(event_id, ticket_class_id))

    def get_event_discounts(self, event_id):
        """
        Returns a paginated response with a key of discounts, containing a list of discount.

        GET /events/:id/discounts/
        """
        return self.get("/events/{0}/discounts/".format(event_id))

    def post_event_discount(
            self, event_id,
            discount_code,
            discount_amount_off=None,
            discount_percent_off=None,
            discount_ticket_ids=None,
            discount_quantity_available=None,
            discount_start_date=None,
            discount_end_date=None):
        """
        POST /events/:id/discounts/

            discount_code               string   required    Code to activate discount
            discount_amount_off         unknown  optional    Fixed reduction amount
            discount_percent_off        string   optional    Percentage reduction
            discount_ticket_ids         unknown  optional    IDs of tickets to limit discount to
            discount_quantity_available integer  optional    Number of discount uses
            discount_start_date         datetime optional    Allow use from this date
            discount_end_date           datetime optional    Allow use until this date

            TODO: Consider deprecating this method
        """
        data = construct_namespaced_dict("discount", locals())
        return self.post("/events/{0}/discounts/".format(event_id), data=data)

    def get_event_discount_by_id(self, event_id, discount_id):
        """
        GET /events/:id/discounts/:id/
        """
        return self.get("/events/{0}/discounts/{1}/".format(
            event_id, discount_id))

    def post_event(self, data):

        return self.post("/events/", data=data)

    def publish_event(self, event_id):

        return self.post("/events/%s/publish/" % event_id)

    def unpublish_event(self, event_id):

        return self.post("/events/%s/unpublish/" % event_id)

    def post_event_ticket_class(self, event_id, data):
        return self.post("/events/{0}/ticket_classes/".format(event_id), data=data)

    def event_search(self, **data):
        # Resolves the search result response problem
        return self.get("/events/search/", data=data)

    def webhook_to_object(self, webhook):
        """
        Converts JSON sent by an Eventbrite Webhook to the appropriate
        Eventbrite object.

        # TODO - Add capability to handle Django request objects
        """
        if isinstance(webhook, string_type):
            # If still JSON, convert to a Python dict
            webhook = json.dumps(webhook)

        # if a flask.Request object, try to convert that to a webhook
        if not isinstance(webhook, dict):
            webhook = get_webhook_from_request(webhook)

        try:
            webhook['api_url']
        except KeyError:
            raise InvalidWebhook

        payload = self.get(webhook['api_url'])

        return payload
