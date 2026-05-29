"""
Runtime patches for wagtail-transfer 0.11.

When importing pages, an Objective is occasionally constructed with a Page
subclass (e.g. pages.RootPage) instead of the base wagtailcore.Page. The
import context's uids_by_source / destination_ids_by_source dicts are keyed
by base model, so the subclass lookup raises KeyError in
Objective._find_at_destination.

Every other call site in wagtail-transfer normalizes via get_base_model() —
this patch closes the one gap that leaks the subclass through.
"""
from wagtail_transfer.models import get_base_model
from wagtail_transfer.operations import Objective

_original_init = Objective.__init__


def _patched_init(self, model, source_id, context, must_update=False):
    _original_init(self, get_base_model(model), source_id, context, must_update)


Objective.__init__ = _patched_init
