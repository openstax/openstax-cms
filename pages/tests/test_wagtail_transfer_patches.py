"""Tests for the wagtail-transfer Objective base-model monkeypatch."""
from django.test import TestCase

from wagtail_transfer.models import get_base_model
from wagtail_transfer.operations import Objective

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
