from django.conf import settings
from social.backends.oauth import BaseOAuth2
from urllib.parse import urlencode
import json
import urllib


class OpenStaxOAuth2(BaseOAuth2):
    """openstax OAuth authentication backend"""
    name = 'openstax'
    AUTHORIZATION_URL = settings.AUTHORIZATION_URL 
    ACCESS_TOKEN_URL = settings.ACCESS_TOKEN_URL 
    USER_QUERY = settings.USER_QUERY
    REQUEST_TOKEN_METHOD = 'POST'
    ACCESS_TOKEN_METHOD = 'POST'
    SCOPE_SEPARATOR = ','
    EXTRA_DATA = [
        ('id', 'id'),
    ]

    def get_user_details(self, response):
        """Return user details from openstax account's"""
        return {'id': response.get('id'),
                'username': response.get('username'),
                'first_name':response.get('first_name'),
                'last_name':response.get('last_name'),
                'full_name': response.get('full_name'),}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = self.USER_QUERY + urlencode({
            'access_token': access_token
        })
        try:
            return json.loads(self.urlopen(url))
        except ValueError:
            return None

    def urlopen(self,url):
        with urllib.request.urlopen(url) as f:
            response = f.read()
        return response.decode("utf-8")
