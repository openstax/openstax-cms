import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from oxauth.functions import get_token, get_user_info


class AccountsTestCase(TestCase):
    def setUp(self):
        self.token = get_token()
        self.client = Client()

    def test_accounts_contains_uuid(self):
        url = settings.USERS_QUERY + urlencode({
            'q': 'id:{}'.format("2"),
            'access_token': self.token['access_token']
        })

        with urlopen(url) as url:
            data = json.loads(url.read().decode())
            uuid = data['items'][0]['uuid']

        self.assertEqual(uuid, "aaa560a1-e828-48fb-b9a8-d01e9aec71d0")

    def test_can_get_user_info(self):
        user_data = get_user_info(2)
        self.assertNotEqual(user_data, False)

    def test_user_data_returns_false_when_invalid(self):
        user_data = get_user_info('asdf')
        self.assertEqual(user_data, False)

    def test_oauth_login_url(self):
        response = self.client.get(reverse('social:begin', args=['openstax']))
        self.assertNotEqual(response.status_code, 404)
