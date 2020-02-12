# -*- coding: utf-8 -*-
import pprint


class EventbriteObject(dict):

    is_list = None
    is_paginated = None
    # pagination dict w/ keys: object_count, page_number, page_size, page_count
    pagination = None
    type = ""
    id = None
    pk = None

    @classmethod
    def create(cls, response):
        data = response.json()
        evbobject = cls(data)
        try:
            # Strip out URL parameters for resource_uri
            evbobject.resource_uri = response.url[:response.url.index('?')]
        except ValueError:
            evbobject.resource_uri = response.url
        evbobject.ok = response.ok
        evbobject.elapsed = response.elapsed
        evbobject.headers = response.headers
        evbobject.reason = response.reason
        evbobject.status_code = response.status_code
        evbobject.request = response.request
        # if it's paginated, it's a list, otherwise we don't know yet
        evbobject.pagination = data.get('pagination', False)
        evbobject.is_list = bool(evbobject.pagination)  # evbobject.is_paginated = True
        evbobject.is_paginated = bool(evbobject.pagination)
        evbobject.pk = evbobject.id = data.get('id')
        evbobject.pagination = data.get('pagination')
        return evbobject

    @property
    def pretty(self):
        return pprint.pformat(self)
