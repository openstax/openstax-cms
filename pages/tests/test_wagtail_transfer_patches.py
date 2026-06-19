"""Tests for the wagtail-transfer Objective base-model monkeypatch."""
import json

from django.test import TestCase

from wagtail_transfer.models import get_base_model
from wagtail_transfer.operations import ImportPlanner, Objective

from openstax.wagtail_transfer_patches import apply_patches


class ObjectivePatchTests(TestCase):
    def test_patch_normalizes_page_subclass_to_base_model(self):
        from pages.models import RootPage

        # ready() already applied it; assert it's installed and idempotent.
        apply_patches()

        # Objective.__init__ only stores attributes, so no DB row is needed.
        objective = Objective(RootPage, 1, context=None)
        # Without the patch, objective.model would be RootPage and the
        # uids_by_source lookup (keyed by base model) would KeyError.
        self.assertIs(objective.model, get_base_model(RootPage))


# A Django/nginx HTTP error page — what the wagtail-transfer source returns on a
# failed digest check, a missing page, or an allowlist rejection. The importer's
# add_json() json-parses the response body blindly, so without a guard this
# surfaces as an opaque JSONDecodeError instead of the real cause.
HTML_403 = (
    b'\n<!doctype html>\n<html lang="en">\n<head>\n  <title>403 Forbidden</title>\n'
    b'</head>\n<body>\n  <h1>403 Forbidden</h1><p></p>\n</body>\n</html>\n'
)
# The headless openstax.org frontend shell — what a 404 from the CMS resolves to
# when the export request lands on the SPA fallback rather than Django.
SPA_SHELL_404 = (
    b'<!doctype html><html lang="en-US"><head><title>OpenStax</title>'
    b'<meta name="description" content="OpenStax offers free college textbooks">'
    b'</head><body></body></html>'
)


class AddJsonGuardTests(TestCase):
    def _importer(self):
        # for_page() only stores attributes; add_json fails (or succeeds) on the
        # payload before any DB access, so no fixtures are needed.
        return ImportPlanner.for_page(source=1, destination=None, source_site='test')

    def test_non_json_response_does_not_raise_opaque_jsondecodeerror(self):
        from openstax.wagtail_transfer_patches import WagtailTransferImportError

        apply_patches()

        with self.assertRaises(WagtailTransferImportError) as ctx:
            self._importer().add_json(HTML_403)

        # The whole point: the caller must not see a bare JSONDecodeError.
        self.assertNotIsInstance(ctx.exception, json.JSONDecodeError)

    def test_error_message_includes_the_source_response_body(self):
        from openstax.wagtail_transfer_patches import WagtailTransferImportError

        apply_patches()

        with self.assertRaises(WagtailTransferImportError) as ctx:
            self._importer().add_json(HTML_403)

        # The source's actual response is the diagnostic — surface it.
        self.assertIn('403 Forbidden', str(ctx.exception))

    def test_spa_shell_response_is_identified_in_the_message(self):
        from openstax.wagtail_transfer_patches import WagtailTransferImportError

        apply_patches()

        with self.assertRaises(WagtailTransferImportError) as ctx:
            self._importer().add_json(SPA_SHELL_404)

        self.assertIn('OpenStax', str(ctx.exception))

    def test_valid_payload_still_parses(self):
        apply_patches()

        # An empty-but-valid payload exercises the wrapped add_json without
        # touching the DB; it must pass straight through the guard.
        payload = json.dumps({'ids_for_import': [], 'mappings': [], 'objects': []})
        self._importer().add_json(payload)  # must not raise
