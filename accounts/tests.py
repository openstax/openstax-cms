import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.test import TestCase
from django.conf import settings

from accounts.functions import get_token


class AccountsTestCase(TestCase):
    def setUp(self):
        pass

    def test_accounts_contains_uuid(self):
        token = get_token()
        url = settings.USERS_QUERY + urlencode({
            'q': 'id:{}'.format("2"),
            'access_token': token['access_token']
        })

        with urlopen(url) as url:
            data = json.loads(url.read().decode())
            uuid = data['items'][0]['uuid']

        self.assertEqual(uuid, "aaa560a1-e828-48fb-b9a8-d01e9aec71d0")
