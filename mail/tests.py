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

    def test_send_redirect_report(self):
        redirects = self.create_fake_redirects()
        mail_func.send_redirect_report(redirects)

    def create_fake_redirects(self):
        redirect = '/l/junk\thttps//:cnx.org\n'
        redirect += '/l/garbage\thttps://cnx.org/contents/HTmjSAcf@2.61:rrzms6rP@2/Introduction\n'
        redirect += '/l/refuse\thttps://openstax.org/openstax-tutor\n'
        redirect += '/r/trash\thttps://trello.com/b/20yf8veQ/devops-go\n'
        return redirect
