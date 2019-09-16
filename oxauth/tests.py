import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from oxauth.functions import get_token, get_user_info
from oxauth.views import login, get_user_data, logout
from .auth import OXSessionDecryptor


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_can_get_user_info(self):
        user_data = get_user_info(2)
        self.assertNotEqual(user_data, False)

    def test_user_info_returns_false_with_no_uid(self):
        user_data = get_user_info()
        self.assertEqual(user_data, False)

    def test_user_data_returns_false_when_invalid(self):
        user_data = get_user_info('asdf')
        self.assertEqual(user_data, False)

    def test_oauth_login_url(self):
        response = self.client.get(reverse('social:begin', args=['openstax']))
        self.assertNotEqual(response.status_code, 404)

    def test_login(self):
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, "/accounts/login/", fetch_redirect_response=False)

        response = self.client.get(reverse('login') + "?next=foo")
        self.assertRedirects(response, "/accounts/login/?r=foo", fetch_redirect_response=False)

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, "/accounts/logout/", fetch_redirect_response=False)

        response = self.client.get(reverse('logout') + "?next=foo")
        self.assertRedirects(response, "/accounts/logout/?r=foo", fetch_redirect_response=False)

    def test_user_notloggedin(self):
        response = self.client.get(reverse('user'))

        response_readable = json.loads(response.content.decode())

        self.assertNotEqual(response.status_code, 404)
        self.assertIn("decryption", response_readable)
        self.assertIn("logged_in", response_readable)
        self.assertIn("cookie", response_readable)
        self.assertIn("validation", response_readable)


    # TODO: Fix the validation, and run the validation function as well.
    # def test_validate_cookie(self):
    #     decryptor = OXSessionDecryptor(secret_key_base="ea068a28cbe16b01fc22c2151c9d00a9883d772e178a05daa6469d4b531200cf168b091c1f551282ab8863715f5f4af72c87799ba85c99d6184436858a390e1d", encrypted_cookie_salt="encrypted cookie", encrypted_signed_cookie_salt="signed encrypted cookie")
    #     cookie = "WmwwcDBlNmVhRmRTVGlwUFErTVZTL0FBOWE1VERZS1gvNE82dTFrSTR0TDNHL1VsRVVDTGExSUc4UFh0Z2h2UUxDKzE2RitBVVg5LzRqQkpuQ09ZUHlIWlBkME8zdHZUSStETHdoS1ZkR1VmVm0rQUhBTlFJS3VBbUZDbGh3c3BtSkQzTXlaNk00UCtISHJjcnhIeDV3Z0RORGZKZG91QzE3cnR4VzhvSnlKa0tNdGwrQTBTZkp4Z0c1cHJiS3FGS2Nhakw1ejFmM3F4ajhYbWtGNlZwQjVRNjdZYWJvSUozd0xGYk5JMEVDRWZWNlp0VHBsbE5KT0VodW1icFF6UHNCRzI1NHZrZzdGYWZnelRhcGk2WHQ0T1ZxdTYzckcyRWZlZ1pWWGpDVXNZVGFPeUViUWVrSGJ3YXlNcVo5UnI0Nnp2Q0U2V2lGWUd0bWNOQVg1NHdKa0EzTFlFZlkzUCt0YUlaK0xUczVOYU5pRE16Z3RqWlRZV1YwYzJvdzhNWXZmUGtRTnFFSVV0dDNGWStDMm91alEvRVd0YXNESkpJNzE5Y1liZ3k3L3lUdnFkWGdoUE9ENDBXRlA3Y0hWbFQ5cDJvRXUxdk1zQ2dYdTQvbmg1SDJkU1hPZnNZUkpOS2VnVnVFOGNmSWVvSHFQNmErNDF2NXZCVkVqeklqUUtJMVYxNGNHUk1XN1RmUXRsS1BOOWUyNjU5ZG02ZC9sWmxLU2ZMdmtpSU56Q0VzRlNWSVBWUXE2UnFDbUpCZndFLS1RV3RyQUYxMmw2ZWhOWGs4UXNqSGJBPT0%3D--1b058a0d696c016fae58f207bdbae1db6df8c312"
    #     validate = decryptor.validate_cookie(cookie)
    #     self.assertEqual(validate, True)

    def test_decrypt_cookie(self):
        decryptor = OXSessionDecryptor(secret_key_base="ea068a28cbe16b01fc22c2151c9d00a9883d772e178a05daa6469d4b531200cf168b091c1f551282ab8863715f5f4af72c87799ba85c99d6184436858a390e1d", encrypted_cookie_salt="encrypted cookie", encrypted_signed_cookie_salt="signed encrypted cookie")
        cookie = "WmwwcDBlNmVhRmRTVGlwUFErTVZTL0FBOWE1VERZS1gvNE82dTFrSTR0TDNHL1VsRVVDTGExSUc4UFh0Z2h2UUxDKzE2RitBVVg5LzRqQkpuQ09ZUHlIWlBkME8zdHZUSStETHdoS1ZkR1VmVm0rQUhBTlFJS3VBbUZDbGh3c3BtSkQzTXlaNk00UCtISHJjcnhIeDV3Z0RORGZKZG91QzE3cnR4VzhvSnlKa0tNdGwrQTBTZkp4Z0c1cHJiS3FGS2Nhakw1ejFmM3F4ajhYbWtGNlZwQjVRNjdZYWJvSUozd0xGYk5JMEVDRWZWNlp0VHBsbE5KT0VodW1icFF6UHNCRzI1NHZrZzdGYWZnelRhcGk2WHQ0T1ZxdTYzckcyRWZlZ1pWWGpDVXNZVGFPeUViUWVrSGJ3YXlNcVo5UnI0Nnp2Q0U2V2lGWUd0bWNOQVg1NHdKa0EzTFlFZlkzUCt0YUlaK0xUczVOYU5pRE16Z3RqWlRZV1YwYzJvdzhNWXZmUGtRTnFFSVV0dDNGWStDMm91alEvRVd0YXNESkpJNzE5Y1liZ3k3L3lUdnFkWGdoUE9ENDBXRlA3Y0hWbFQ5cDJvRXUxdk1zQ2dYdTQvbmg1SDJkU1hPZnNZUkpOS2VnVnVFOGNmSWVvSHFQNmErNDF2NXZCVkVqeklqUUtJMVYxNGNHUk1XN1RmUXRsS1BOOWUyNjU5ZG02ZC9sWmxLU2ZMdmtpSU56Q0VzRlNWSVBWUXE2UnFDbUpCZndFLS1RV3RyQUYxMmw2ZWhOWGs4UXNqSGJBPT0%3D--1b058a0d696c016fae58f207bdbae1db6df8c312"
        decrypted = decryptor.get_cookie_data(cookie)
        self.assertEqual('session_id' in decrypted, True)
