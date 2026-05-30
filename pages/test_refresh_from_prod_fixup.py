"""Tests for the refresh_from_prod_fixup management command."""
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from salesforce.models import Partner, SalesforceForms
from snippets.models import SharedContent
from wagtail.models import Site


class RefreshFromProdFixupTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.site.hostname = 'openstax.org'
        self.site.save()

        self.snippet = SharedContent.objects.create(
            title='Test',
            heading='Heading',
            content='Visit https://openstax.org/subjects for more.',
            button_url='https://openstax.org/give',
        )

    def _call(self, *extra_args):
        out = StringIO()
        call_command(
            'refresh_from_prod_fixup',
            '--target-host', 'dev.openstax.org',
            *extra_args,
            stdout=out,
        )
        return out.getvalue()

    def test_dry_run_does_not_persist(self):
        output = self._call()
        self.snippet.refresh_from_db()
        self.site.refresh_from_db()
        self.assertEqual(self.snippet.button_url, 'https://openstax.org/give')
        self.assertEqual(self.site.hostname, 'openstax.org')
        self.assertIn('[DRY RUN]', output)

    def test_commit_rewrites_url_and_text_fields_and_site(self):
        self._call('--commit')
        self.snippet.refresh_from_db()
        self.site.refresh_from_db()
        self.assertEqual(self.snippet.button_url, 'https://dev.openstax.org/give')
        self.assertEqual(
            self.snippet.content,
            'Visit https://dev.openstax.org/subjects for more.',
        )
        self.assertEqual(self.site.hostname, 'dev.openstax.org')

    def test_second_run_is_idempotent(self):
        self._call('--commit')
        self._call('--commit')  # second run on already-rewritten data
        self.snippet.refresh_from_db()
        self.assertEqual(self.snippet.button_url, 'https://dev.openstax.org/give')
        # Specifically: no nested-substitution like https://dev.dev.openstax.org
        self.assertNotIn('dev.dev.', self.snippet.button_url)
        self.assertNotIn('dev.dev.', self.snippet.content)

    def test_refuses_when_source_equals_target(self):
        with self.assertRaises(CommandError):
            call_command(
                'refresh_from_prod_fixup',
                '--target-host', 'openstax.org',
                '--commit',
                stdout=StringIO(),
            )

    def test_refuses_when_target_is_not_a_hostname(self):
        with self.assertRaises(CommandError):
            call_command(
                'refresh_from_prod_fixup',
                '--target-host', 'localhost',
                '--commit',
                stdout=StringIO(),
            )

    def test_truncates_salesforce_synced_models_leaves_config(self):
        Partner.objects.create(partner_name='Synced Partner', salesforce_id='abc123')
        forms_config = SalesforceForms.objects.create(
            oid='form-oid', posting_url='https://openstax.org/form',
        )
        self._call('--commit')
        # Salesforce-synced data wiped (next sync will repopulate)
        self.assertEqual(Partner.objects.count(), 0)
        # Local config preserved
        forms_config.refresh_from_db()
        self.assertEqual(forms_config.oid, 'form-oid')

    @override_settings(ENVIRONMENT='prod')
    def test_refuses_to_run_on_prod(self):
        with self.assertRaises(CommandError):
            call_command(
                'refresh_from_prod_fixup',
                '--target-host', 'dev.openstax.org',
                '--commit',
                stdout=StringIO(),
            )

