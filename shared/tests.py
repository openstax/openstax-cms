from django.test import TestCase
from shared.test_utilities import mock_user_login, RequestMock

from unittest.mock import MagicMock

class TestMockUserLogin(TestCase):
    def test_mock_user_login(self):
        user = mock_user_login()
        self.assertEqual(user.openstaxuserprofile.openstax_accounts_uuid, '467cea6c-8159-40b1-90f1-e9b0dc26344c')


class TestMockRequest(TestCase):
    def test_create_mock_request(self):
        req = RequestMock()
        self.assertEqual(req.cookies, {})

