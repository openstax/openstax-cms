from django.test import TestCase
from unittest import mock

from django.contrib import admin

from books.constants import RETIRED
from errata.models import Errata, EmailText
from books.models import Book, BookIndex
from pages.models import Page, RootPage
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.documents.models import Document
import datetime



class ErrataTest(TestCase):

    def setUp(self):
        # create root page
        root_page = Page.objects.get(title="Root")
        # create homepage
        homepage = RootPage(title="Hello World",
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


class ActiveBookListFilterTests(TestCase):
    class FakeBookQuerySet(list):
        def order_by(self, *fields):
            self.ordering = fields
            return self

    class FakeBook:
        def __init__(self, pk, title):
            self.pk = pk
            self.title = title

        def __str__(self):
            return self.title

    def test_filter_choices_hide_retired_books(self):
        from errata.admin import ActiveBookListFilter, ErrataAdmin

        request = mock.Mock()
        errata_admin = ErrataAdmin(Errata, admin.site)
        book_field = Errata._meta.get_field("book")
        active_book = self.FakeBook(1, "Active Book")

        fake_queryset = self.FakeBookQuerySet([active_book])
        with mock.patch.object(Book.objects, "exclude", return_value=fake_queryset) as mock_exclude:
            book_filter = ActiveBookListFilter(
                book_field,
                request,
                {},
                Errata,
                errata_admin,
                "book",
            )

        mock_exclude.assert_called_once_with(book_state=RETIRED)
        self.assertEqual(fake_queryset.ordering, ("title",))
        self.assertEqual(book_filter.lookup_choices, [(1, "Active Book")])

    def test_filter_still_accepts_url_parameter_for_retired_books(self):
        from errata.admin import ActiveBookListFilter, ErrataAdmin

        request = mock.Mock()
        errata_admin = ErrataAdmin(Errata, admin.site)
        book_field = Errata._meta.get_field("book")

        with mock.patch.object(Book.objects, "exclude", return_value=self.FakeBookQuerySet()):
            book_filter = ActiveBookListFilter(
                book_field,
                request,
                {"book__page_ptr__exact": "2"},
                Errata,
                errata_admin,
                "book",
            )

        self.assertEqual(
            book_filter.expected_parameters(),
            ["book__page_ptr__exact", "book__isnull"],
        )
        self.assertEqual(book_filter.lookup_val, "2")


class ErrataAdminSharedInstanceTest(TestCase):
    """ErrataAdmin is registered once and reused by Django across every request.
    get_fields/get_readonly_fields/get_list_display must be computed per-request
    rather than assigned to self, or one user's role can leak into another's
    concurrent request. See the comment above these methods in errata/admin.py.
    """

    def test_get_form_is_stable_when_interleaved_with_a_different_role(self):
        from django.test import RequestFactory
        from django.contrib.auth.models import User, Group
        from django.contrib.admin.utils import flatten_fieldsets
        from errata.admin import ErrataAdmin

        rf = RequestFactory()
        errata_admin = ErrataAdmin(Errata, admin.site)

        vendor_group = Group.objects.create(name='Editorial Vendor')
        plain_user = User.objects.create_user('plain', is_staff=True)
        vendor_user = User.objects.create_user('vendor', is_staff=True)
        vendor_user.groups.add(vendor_group)

        plain_request = rf.get('/errata/add/')
        plain_request.user = plain_user
        vendor_request = rf.get('/errata/add/')
        vendor_request.user = vendor_user

        # Mirrors Django's own _changeform_view: get_fieldsets() runs for one
        # user, then get_form() runs for a *different* user before the first
        # request finishes - the interleaving that produced the "Unknown
        # field(s) specified for Errata" 500s in production.
        errata_admin.get_form(plain_request, None)
        fieldsets = errata_admin.get_fieldsets(vendor_request, None)
        form_class = errata_admin.get_form(vendor_request, None, fields=flatten_fieldsets(fieldsets))

        self.assertIsNotNone(form_class)


class ErrataAdminRolesTest(TestCase):
    """Verifies the role model in
    docs/superpowers/specs/2026-07-10-errata-admin-permissions-design.md:
    Super Admin (is_superuser), Internal Editor ('Content Managers' group,
    or superuser), and everyone else treated as Editorial Vendor tier
    (least-privilege default - not just the named 'Editorial Vendor' group).
    """

    def setUp(self):
        from django.test import RequestFactory
        from django.contrib.auth.models import User, Group
        from errata.admin import ErrataAdmin

        self.factory = RequestFactory()
        self.errata_admin = ErrataAdmin(Errata, admin.site)

        self.super_admin = User.objects.create_user(
            'super_admin', is_staff=True, is_superuser=True
        )

        content_managers = Group.objects.create(name='Content Managers')
        self.internal_editor = User.objects.create_user('internal_editor', is_staff=True)
        self.internal_editor.groups.add(content_managers)

        vendor_group = Group.objects.create(name='Editorial Vendor')
        self.vendor = User.objects.create_user('vendor', is_staff=True)
        self.vendor.groups.add(vendor_group)

        # No group, not superuser - the least-privilege fallback case.
        self.unassigned_staff = User.objects.create_user('unassigned_staff', is_staff=True)

    def _request_as(self, user):
        request = self.factory.get('/errata/errata/add/')
        request.user = user
        return request

    def test_super_admin_sees_accounts_link_and_can_delete(self):
        request = self._request_as(self.super_admin)
        self.assertIn('accounts_link', self.errata_admin.get_fields(request))
        self.assertIn('accounts_link', self.errata_admin.get_readonly_fields(request))
        self.assertTrue(self.errata_admin.has_delete_permission(request))

    def test_internal_editor_sees_accounts_link_but_cannot_delete(self):
        request = self._request_as(self.internal_editor)
        self.assertIn('accounts_link', self.errata_admin.get_fields(request))
        self.assertIn('accounts_link', self.errata_admin.get_readonly_fields(request))
        self.assertFalse(self.errata_admin.has_delete_permission(request))

    def test_vendor_does_not_see_accounts_link_and_cannot_delete(self):
        request = self._request_as(self.vendor)
        self.assertNotIn('accounts_link', self.errata_admin.get_fields(request))
        self.assertNotIn('accounts_link', self.errata_admin.get_readonly_fields(request))
        self.assertFalse(self.errata_admin.has_delete_permission(request))

    def test_unassigned_staff_is_treated_as_vendor_tier(self):
        request = self._request_as(self.unassigned_staff)
        self.assertNotIn('accounts_link', self.errata_admin.get_fields(request))
        self.assertFalse(self.errata_admin.has_delete_permission(request))

    def test_super_admin_and_internal_editor_get_identical_fields(self):
        super_admin_fields = self.errata_admin.get_fields(self._request_as(self.super_admin))
        internal_editor_fields = self.errata_admin.get_fields(self._request_as(self.internal_editor))
        self.assertEqual(super_admin_fields, internal_editor_fields)

    def test_bulk_status_actions_are_internal_only(self):
        internal_actions = self.errata_admin.get_actions(self._request_as(self.internal_editor))
        vendor_actions = self.errata_admin.get_actions(self._request_as(self.vendor))
        unassigned_actions = self.errata_admin.get_actions(self._request_as(self.unassigned_staff))
        for action_name in ('mark_in_review', 'mark_reviewed', 'mark_archived', 'mark_completed'):
            self.assertIn(action_name, internal_actions)
            self.assertNotIn(action_name, vendor_actions)
            self.assertNotIn(action_name, unassigned_actions)

    def test_delete_selected_only_available_to_users_with_delete_permission(self):
        super_admin_actions = self.errata_admin.get_actions(self._request_as(self.super_admin))
        internal_editor_actions = self.errata_admin.get_actions(self._request_as(self.internal_editor))
        self.assertIn('delete_selected', super_admin_actions)
        self.assertNotIn('delete_selected', internal_editor_actions)


class ErrataPostHogCaptureTest(TestCase):
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
