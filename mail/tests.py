import json
import mail.functions as mail_func

from django.middleware import csrf
from django.test import Client, TestCase
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash

from mail.models import Mail


class MailTest(TestCase):

    def setUp(self):
        Mail.objects.create(subject="Bulk Order", to_address="noreply@openstax.org")
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test_can_create_mail(self):
        mail = Mail.objects.create(subject="Test Email", to_address="test@openstax.org")
        self.assertEqual("Test Email", mail.subject)

    def test_get_csrf_token(self):
        # testing that csrf token is returned on GET request to mail api
        response = self.client.get('/api/mail/send_mail/')
        request = response.wsgi_request
        csrf_token = csrf.get_token(request)

    def test_send(self):
        response = self.client.post('/apps/cms/api/mail/send_mail/', {'to_address': 'noreply@openstax.org',
                                                             'from_name': 'Openstax',
                                                             'from_address': 'noreply@openstax.org',
                                                             'subject': 'Test Subject',
                                                             'message_body': 'This is a test.'})

        self.assertRedirects(
            response, '/confirmation/contact', target_status_code=301, fetch_redirect_response=False)

    def send_bulk_order_email(self):
        response = self.client.post('/api/mail/send_mail/', {'to_address': 'noreply@openstax.org',
                                                             'from_name': 'Openstax',
                                                             'from_address': 'noreply@openstax.org',
                                                             'subject': 'Bulk Order',
                                                             'message_body': 'Send me a bulk order of books, please!'})
        self.assertRedirects(
            response, '/confirmation/bulk-order', target_status_code=301, fetch_redirect_response=False)

    def test_send_redirect_report(self):
        redirects = self.create_fake_redirects()
        mail_func.send_redirect_report(redirects)

    def create_fake_redirects(self):
        redirect = '/l/junk\thttps//:cnx.org\n'
        redirect += '/l/garbage\thttps://cnx.org/contents/HTmjSAcf@2.61:rrzms6rP@2/Introduction\n'
        redirect += '/l/refuse\thttps://openstax.org/openstax-tutor\n'
        redirect += '/r/trash\thttps://trello.com/b/20yf8veQ/devops-go\n'
        return redirect

    def test_slashless_apis_are_good(self):
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/mail/send_mail')
