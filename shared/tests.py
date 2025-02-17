from django.test import TestCase
from shared.test_utilities import mock_user_login, RequestMock


class TestMockRequest(TestCase):
    def test_create_mock_request(self):
        req = RequestMock()
        self.assertEqual(req.cookies, {})

