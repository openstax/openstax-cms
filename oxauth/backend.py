import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings
from social_core.backends.oauth import BaseOAuth2


class OpenStax(BaseOAuth2):

    """openstax OAuth authentication backend"""
    name = 'openstax'
    ID_KEY = 'id'
    AUTHORIZATION_URL = settings.AUTHORIZATION_URL
    ACCESS_TOKEN_URL = settings.ACCESS_TOKEN_URL
    USER_QUERY = settings.USER_QUERY
    REQUEST_TOKEN_METHOD = 'POST'
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id'),
    ]

    def get_user_details(self, response):
        """Return user details from openstax account's"""
        contact_infos = response.get('contact_infos')
        try:
            email = contact_infos[0]['value']
        except IndexError:
            email = "none@openstax.org"
        return {'username': str(response.get('id')),
                'email': email,
                'first_name': response.get('first_name'),
                'last_name': response.get('last_name'),
                'full_name': response.get('full_name'), }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = self.USER_QUERY + urlencode({
            'access_token': access_token
        })
        try:
            return json.loads(self.urlopen(url))
        except ValueError:
            return None

    def urlopen(self, url):
        with urlopen(url) as f:
            response = f.read()
        return response.decode("utf-8")
