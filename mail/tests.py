import json

from django.middleware import csrf
from django.test import Client, TestCase


class MailTest(TestCase):

    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test_get_csrf_token(self):
        # testing that csrf token is returned on GET request to mail api
        response = self.client.get('/api/mail/send_mail/')
        request = response.wsgi_request
        csrf_token = csrf.get_token(request)

    def test_send(self):
        response = self.client.post('/api/mail/send_mail/', {'to_address': 'noreply@openstax.org',
                                                             'from_name': 'Openstax',
                                                             'from_address': 'noreply@openstax.org',
                                                             'subject': 'Test Subject',
                                                             'message_body': 'This is a test.'})
        self.assertRedirects(
            response, '/confirmation/contact', target_status_code=301)
