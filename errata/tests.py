from django.test import TestCase
from unittest import mock

from errata.models import Errata, EmailText
from books.models import Book, BookIndex
from pages.models import Page, HomePage
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.documents.models import Document
import datetime

DjangoTestCase = TestCase


class ErrataTest(TestCase):

    def setUp(self):
        # create root page
        root_page = Page.objects.get(title="Root")
        # create homepage
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        # add homepage to root page
        root_page.add_child(instance=homepage)
        # create book index page
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test",
                               )
        # add book index to homepage
        homepage.add_child(instance=book_index)
        # create book (finally! needed for Errata reports)
        test_image = SimpleUploadedFile(name='openstax.png', content=open("pages/static/images/openstax.png", 'rb').read())
        test_doc = Document.objects.create(title='Test Doc', file=test_image)
        book = Book(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d',
                            title='University Physics',
                            salesforce_abbreviation='University Phys (Calc)',
                            salesforce_name='University Physics',
                            description="Test Book",
                            cover=test_doc,
                            title_image=test_doc,
                            publish_date=datetime.date.today(),
                            locale=root_page.locale
                            )
        book_index.add_child(instance=book)

    def test_can_create_errata(self):
        EmailText.objects.create(
            email_case = 'Created in Fall',
            email_subject_text = "test",
            email_body_text = "test",
            notes = "test",
        )
        EmailText.objects.create(
            email_case = 'Created in Spring',
            email_subject_text = "test",
            email_body_text = "test",
            notes = "test",
        )
        errata = Errata.objects.create(
            book=Book.objects.get(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d'),
            detail="This is a test.",
        )
        self.assertEqual("New", errata.status)


class ErrataPostHogCaptureTest(DjangoTestCase):
    def _instance(self, account_id=None):
        return mock.Mock(
            submitted_by_account_id=account_id,
            book_id=1,
            book=mock.Mock(title='Biology 2e'),
            error_type='Typo',
        )

    @mock.patch('errata.models.posthog_capture')
    def test_no_capture_on_update(self, mock_capture):
        from errata.models import capture_errata_submitted
        capture_errata_submitted(sender=None, instance=self._instance(), created=False)
        mock_capture.assert_not_called()

    @mock.patch('errata.models.get_user_info', return_value={'uuid': 'uuid-9', 'email': 'a@b.co'})
    @mock.patch('errata.models.posthog_capture')
    def test_capture_identified_on_create(self, mock_capture, _mock_user):
        from errata.models import capture_errata_submitted
        capture_errata_submitted(sender=None, instance=self._instance(account_id=42), created=True)
        mock_capture.assert_called_once()
        kwargs = mock_capture.call_args.kwargs
        self.assertEqual(kwargs['distinct_id'], 'uuid-9')
        self.assertEqual(kwargs['properties']['form_type'], 'errata')
        self.assertEqual(kwargs['properties']['book'], 'Biology 2e')

    @mock.patch('errata.models.posthog_capture')
    def test_capture_anonymous_when_no_account(self, mock_capture):
        from errata.models import capture_errata_submitted
        capture_errata_submitted(sender=None, instance=self._instance(account_id=None), created=True)
        kwargs = mock_capture.call_args.kwargs
        self.assertIsNone(kwargs['distinct_id'])
