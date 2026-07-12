from django.test import TestCase
from unittest import mock

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone

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

    def _create_email_text_fixtures(self):
        EmailText.objects.create(email_case='Created in Fall', email_subject_text="test",
                                  email_body_text="test", notes="test")
        EmailText.objects.create(email_case='Created in Spring', email_subject_text="test",
                                  email_body_text="test", notes="test")

    def test_junk_automatically_archives(self):
        # help_text on Errata.junk promises this; save() didn't actually do it.
        self._create_email_text_fixtures()
        errata = Errata.objects.create(
            book=Book.objects.get(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d'),
            detail="This is junk.",
            junk=True,
        )
        self.assertTrue(errata.archived)

    @mock.patch('errata.models.threading.Thread')
    def test_cache_invalidation_runs_in_background_thread(self, mock_thread_cls):
        from errata.models import invalidate_cloudfront_caches
        self._create_email_text_fixtures()
        Errata.objects.create(
            book=Book.objects.get(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d'),
            detail="This is a test.",
        )
        mock_thread_cls.assert_called_once_with(
            target=invalidate_cloudfront_caches, args=('errata',), daemon=True)
        mock_thread_cls.return_value.start.assert_called_once()


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
    get_fields/get_readonly_fields must be computed per-request
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

        vendor_group, _ = Group.objects.get_or_create(name='Editorial Vendor')
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

        content_managers, _ = Group.objects.get_or_create(name='Content Managers')
        self.internal_editor = User.objects.create_user('internal_editor', is_staff=True)
        self.internal_editor.groups.add(content_managers)

        vendor_group, _ = Group.objects.get_or_create(name='Editorial Vendor')
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
        for action_name in ('mark_in_review', 'mark_OpenStax_editorial_review', 'mark_cartridge_review',
                            'mark_reviewed', 'mark_archived', 'mark_completed'):
            self.assertIn(action_name, internal_actions)
            self.assertNotIn(action_name, vendor_actions)
            self.assertNotIn(action_name, unassigned_actions)

    def test_delete_selected_only_available_to_users_with_delete_permission(self):
        super_admin_actions = self.errata_admin.get_actions(self._request_as(self.super_admin))
        internal_editor_actions = self.errata_admin.get_actions(self._request_as(self.internal_editor))
        self.assertIn('delete_selected', super_admin_actions)
        self.assertNotIn('delete_selected', internal_editor_actions)


class ErrataIndexTest(TestCase):
    """list_filter is heavily used against status/archived/junk/created on a
    table with years of accumulated submissions and no indexes beyond the
    implicit FK ones - every filtered changelist view was a sequential scan."""

    def test_has_indexes_backing_the_common_admin_filters(self):
        index_fields = {tuple(idx.fields) for idx in Errata._meta.indexes}
        self.assertIn(('status',), index_fields)
        self.assertIn(('archived', 'junk'), index_fields)
        self.assertIn(('created',), index_fields)


class ErrataAdminMediaTest(TestCase):
    def test_does_not_load_duplicate_jquery_from_cdn(self):
        from errata.admin import ErrataAdmin
        self.assertNotIn(
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            ErrataAdmin.Media.js,
        )


class ErrataAdminOrderingTest(TestCase):
    def test_default_ordering_is_oldest_first(self):
        from django.test import RequestFactory
        from errata.admin import ErrataAdmin

        errata_admin = ErrataAdmin(Errata, admin.site)
        request = RequestFactory().get('/errata/errata/')
        self.assertEqual(list(errata_admin.get_ordering(request)), ['created'])


class ErrataAdminDefaultQueueFilterTest(TestCase):
    """Changelist should default to hiding archived/junk noise, but an
    explicit ?view=all must still show everything - a hard-filtered
    get_queryset() would have broken that escape hatch."""

    def setUp(self):
        root_page = Page.objects.get(title="Root")
        homepage = RootPage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)
        book_index = BookIndex(title="Book Index", page_description="Test",
                                dev_standard_1_description="Test", dev_standard_2_description="Test",
                                dev_standard_3_description="Test", dev_standard_4_description="Test")
        homepage.add_child(instance=book_index)
        test_image = SimpleUploadedFile(name='openstax.png', content=open("pages/static/images/openstax.png", 'rb').read())
        test_doc = Document.objects.create(title='Test Doc', file=test_image)
        book = Book(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d', title='University Physics',
                    salesforce_abbreviation='University Phys (Calc)', salesforce_name='University Physics',
                    description="Test Book", cover=test_doc, title_image=test_doc,
                    publish_date=datetime.date.today(), locale=root_page.locale)
        book_index.add_child(instance=book)

        EmailText.objects.create(email_case='Created in Fall', email_subject_text="test",
                                  email_body_text="test", notes="test")
        EmailText.objects.create(email_case='Created in Spring', email_subject_text="test",
                                  email_body_text="test", notes="test")

        self.active = Errata.objects.create(book=book, detail="active")
        self.archived = Errata.objects.create(book=book, detail="archived", archived=True)
        self.junk = Errata.objects.create(book=book, detail="junk", junk=True)

    def test_default_hides_archived_and_junk(self):
        from django.test import RequestFactory
        from errata.admin import DefaultActiveQueueFilter

        f = DefaultActiveQueueFilter(RequestFactory().get('/'), {}, Errata, None)
        qs = f.queryset(None, Errata.objects.all())
        self.assertEqual(list(qs), [self.active])

    def test_view_all_shows_everything(self):
        from django.test import RequestFactory
        from errata.admin import DefaultActiveQueueFilter

        # SimpleListFilter expects params in request.GET.lists() shape (a
        # list per key, "last wins") - not a bare string.
        f = DefaultActiveQueueFilter(RequestFactory().get('/'), {'view': ['all']}, Errata, None)
        qs = f.queryset(None, Errata.objects.all())
        self.assertEqual(set(qs), {self.active, self.archived, self.junk})


class ErrataAdminBulkActionsTest(TestCase):
    """mark_* bulk actions used to call queryset.update(), bypassing
    Errata.save() entirely - skipping date auto-stamps, resolution_notes
    autofill, the status-update email signal, and clean()'s
    resolution-required rule. These pin down the per-object .save() path."""

    def setUp(self):
        from django.test import RequestFactory
        from django.contrib.auth.models import User, Group
        from django.contrib.messages.storage.cookie import CookieStorage
        from errata.admin import ErrataAdmin

        self.factory = RequestFactory()
        self.errata_admin = ErrataAdmin(Errata, admin.site)
        self.MessageStorage = CookieStorage

        content_managers, _ = Group.objects.get_or_create(name='Content Managers')
        self.internal_editor = User.objects.create_user('bulk_internal_editor', is_staff=True)
        self.internal_editor.groups.add(content_managers)

        EmailText.objects.create(email_case='Created in Fall', email_subject_text="t", email_body_text="t", notes="t")
        EmailText.objects.create(email_case='Created in Spring', email_subject_text="t", email_body_text="t", notes="t")
        EmailText.objects.create(email_case='Completed and Sent to Customer Support',
                                  email_subject_text="Resolved", email_body_text="body", notes="t")
        EmailText.objects.create(email_case='Reviewed and Approved',
                                  email_subject_text="Reviewed", email_body_text="body", notes="t")

        root_page = Page.objects.get(title="Root")
        homepage = RootPage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)
        book_index = BookIndex(title="Book Index", page_description="Test",
                                dev_standard_1_description="Test", dev_standard_2_description="Test",
                                dev_standard_3_description="Test", dev_standard_4_description="Test")
        homepage.add_child(instance=book_index)
        test_image = SimpleUploadedFile(name='openstax.png', content=open("pages/static/images/openstax.png", 'rb').read())
        test_doc = Document.objects.create(title='Test Doc', file=test_image)
        self.book = Book(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d', title='University Physics',
                          salesforce_abbreviation='University Phys (Calc)', salesforce_name='University Physics',
                          description="Test Book", cover=test_doc, title_image=test_doc,
                          publish_date=datetime.date.today(), locale=root_page.locale)
        book_index.add_child(instance=self.book)

    def _request_as(self, user):
        request = self.factory.post('/errata/errata/')
        request.user = user
        request._messages = self.MessageStorage(request)
        return request

    def test_mark_reviewed_saves_each_object_and_stamps_reviewed_date(self):
        errata = Errata.objects.create(book=self.book, detail="x", is_assessment_errata='No', resolution='Approved')
        self.errata_admin.mark_reviewed(
            self._request_as(self.internal_editor), Errata.objects.filter(pk=errata.pk))
        errata.refresh_from_db()
        self.assertEqual(errata.status, 'Reviewed')
        self.assertIsNotNone(errata.reviewed_date)

    @mock.patch('errata.models.send_mail')
    def test_mark_completed_fires_status_update_email(self, mock_send_mail):
        errata = Errata.objects.create(
            book=self.book, detail="x", is_assessment_errata='No', resolution='Sent to Customer Support')
        self.errata_admin.mark_completed(
            self._request_as(self.internal_editor), Errata.objects.filter(pk=errata.pk))
        mock_send_mail.assert_called_once()

    def test_mark_completed_skips_object_missing_required_resolution(self):
        errata = Errata.objects.create(book=self.book, detail="x", is_assessment_errata='No')
        self.errata_admin.mark_completed(
            self._request_as(self.internal_editor), Errata.objects.filter(pk=errata.pk))
        errata.refresh_from_db()
        self.assertEqual(errata.status, 'New')


class ErrataPermissionGroupsMigrationTest(TestCase):
    """errata/migrations/0057_create_errata_permission_groups.py must create
    both groups with sane defaults on a fresh database, and must never
    clobber a group's permissions if it already exists (that's exactly how
    the 2026-07-10 incident happened - a hand-edited group with no code
    review or environment parity)."""

    def test_creates_groups_with_default_permissions(self):
        import importlib
        from types import SimpleNamespace
        from django.apps import apps as global_apps
        from django.contrib.auth.models import Group
        from django.db import connection

        migration = importlib.import_module(
            'errata.migrations.0057_create_errata_permission_groups'
        )

        Group.objects.filter(name__in=['Content Managers', 'Editorial Vendor']).delete()

        migration.create_errata_permission_groups(
            global_apps, SimpleNamespace(connection=connection))

        expected_codenames = {'add_errata', 'change_errata', 'view_errata'}
        content_managers = Group.objects.get(name='Content Managers')
        vendor = Group.objects.get(name='Editorial Vendor')
        self.assertEqual(
            set(content_managers.permissions.values_list('codename', flat=True)),
            expected_codenames,
        )
        self.assertEqual(
            set(vendor.permissions.values_list('codename', flat=True)),
            expected_codenames,
        )

    def test_does_not_clobber_an_existing_groups_permissions(self):
        import importlib
        from types import SimpleNamespace
        from django.apps import apps as global_apps
        from django.contrib.auth.models import Group, Permission
        from django.db import connection

        migration = importlib.import_module(
            'errata.migrations.0057_create_errata_permission_groups'
        )

        content_managers, _ = Group.objects.get_or_create(name='Content Managers')
        delete_perm = Permission.objects.get(
            content_type__app_label='errata',
            content_type__model='errata',
            codename='delete_errata',
        )
        content_managers.permissions.set([delete_perm])

        migration.create_errata_permission_groups(
            global_apps, SimpleNamespace(connection=connection))

        content_managers.refresh_from_db()
        self.assertEqual(
            set(content_managers.permissions.values_list('codename', flat=True)),
            {'delete_errata'},
        )


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


class ErrataChangelistObjectToolsTest(TestCase):
    """The custom change_list_template must extend reversion's own
    change_list.html, not stock admin/change_list.html directly - otherwise
    it silently drops VersionAdmin's "Recover deleted errata list" link
    while still adding the new Dashboard link."""

    def setUp(self):
        from django.contrib.auth.models import User
        self.superuser = User.objects.create_superuser('changelist_super', 'x@example.com', 'pass12345')

    def test_changelist_keeps_recover_link_and_adds_dashboard_link(self):
        self.client.force_login(self.superuser)
        response = self.client.get('/django-admin/errata/errata/')
        self.assertContains(response, 'Recover deleted errata list')
        self.assertContains(response, 'href="dashboard/"')


class ErrataDashboardTest(TestCase):
    """Read-only stats page (status funnel, resolution time, staleness,
    per-book counts) so staff can see the impact of review work - gated on
    the app's own view_errata permission, not just generic admin access."""

    def setUp(self):
        from django.contrib.auth.models import User, Group

        root_page = Page.objects.get(title="Root")
        homepage = RootPage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)
        book_index = BookIndex(title="Book Index", page_description="Test",
                                dev_standard_1_description="Test", dev_standard_2_description="Test",
                                dev_standard_3_description="Test", dev_standard_4_description="Test")
        homepage.add_child(instance=book_index)
        test_image = SimpleUploadedFile(name='openstax.png', content=open("pages/static/images/openstax.png", 'rb').read())
        test_doc = Document.objects.create(title='Test Doc', file=test_image)
        self.book = Book(cnx_id='d50f6e32-0fda-46ef-a362-9bd36ca7c97d', title='University Physics',
                          salesforce_abbreviation='University Phys (Calc)', salesforce_name='University Physics',
                          description="Test Book", cover=test_doc, title_image=test_doc,
                          publish_date=datetime.date.today(), locale=root_page.locale)
        book_index.add_child(instance=self.book)

        EmailText.objects.create(email_case='Created in Fall', email_subject_text="t", email_body_text="t", notes="t")
        EmailText.objects.create(email_case='Created in Spring', email_subject_text="t", email_body_text="t", notes="t")
        EmailText.objects.create(email_case='Reviewed and Approved', email_subject_text="t", email_body_text="t", notes="t")

        content_managers, _ = Group.objects.get_or_create(name='Content Managers')
        self.viewer = User.objects.create_user('dash_viewer', is_staff=True)
        self.viewer.groups.add(content_managers)

    def test_requires_view_errata_permission(self):
        from django.contrib.auth.models import User
        outsider = User.objects.create_user('dash_outsider', is_staff=True)
        self.client.force_login(outsider)
        response = self.client.get(reverse('admin:errata_errata_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_shows_status_funnel_counts(self):
        Errata.objects.create(book=self.book, detail="a")
        Errata.objects.create(book=self.book, detail="b", is_assessment_errata='No',
                               resolution='Approved', status='Reviewed')
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('admin:errata_errata_dashboard'))
        self.assertEqual(response.status_code, 200)
        funnel = {row['label']: row['count'] for row in response.context['funnel']}
        self.assertEqual(funnel['New'], 1)
        self.assertEqual(funnel['Reviewed'], 1)

    def test_computes_average_resolution_days(self):
        errata = Errata.objects.create(book=self.book, detail="a")
        Errata.objects.filter(pk=errata.pk).update(
            created=timezone.now() - datetime.timedelta(days=10),
            resolution_date=timezone.now().date(),
        )
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('admin:errata_errata_dashboard'))
        self.assertEqual(response.context['avg_resolution_days'], 10.0)

    def test_lists_oldest_open_items_first(self):
        older = Errata.objects.create(book=self.book, detail="older")
        Errata.objects.filter(pk=older.pk).update(created=timezone.now() - datetime.timedelta(days=5))
        Errata.objects.create(book=self.book, detail="newer")
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('admin:errata_errata_dashboard'))
        oldest_open_ids = [e.pk for e in response.context['oldest_open']]
        self.assertEqual(oldest_open_ids[0], older.pk)
