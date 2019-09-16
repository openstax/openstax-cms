from django.test import TestCase
from django.test.utils import override_settings

class AccountsTestCase(TestCase):

    @override_settings(ACCOUNTS_SERVER_URL='https://fakeaccounts.org')
    def test_accounts_redirects_to_accounts_server_url(self):
        path = "/accounts/login?blah=whatever"
        response = self.client.get(path)
        self.assertRedirects(response,
                             "https://fakeaccounts.org{}".format(path),
                             fetch_redirect_response=False)
