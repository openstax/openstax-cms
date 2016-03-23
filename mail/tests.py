from django.test import TestCase, Client


class MailTest(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test_send(self):
        response = self.client.post('/api/mail/send_mail/', {'to_address': 'noreply@openstax.org',
                                                             'from_name': 'Openstax',
                                                             'from_address': 'noreply@openstax.org',
                                                             'subject': 'Test Subject',
                                                             'message_body': 'This is a test.'})
        self.assertRedirects(response, '/contact-thank-you', target_status_code=301)
