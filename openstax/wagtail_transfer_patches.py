"""
Runtime patches for wagtail-transfer 0.11.

When importing pages, an Objective is occasionally constructed with a Page
subclass (e.g. pages.RootPage) instead of the base wagtailcore.Page. The
import context's uids_by_source / destination_ids_by_source dicts are keyed
by base model, so the subclass lookup raises KeyError in
Objective._find_at_destination (operations.py: `uids_by_source[(self.model,
self.source_id)]`). Objective.__eq__/__hash__ also key on self.model, so
normalizing in __init__ additionally fixes set-dedup of objectives.

Every other call site in wagtail-transfer normalizes via get_base_model() —
this patch closes the one gap that leaks the subclass through. Upstream issue:
https://github.com/wagtail/wagtail-transfer/issues/127 (open as of 0.11).

`apply_patches()` is idempotent and is called from
global_settings.apps.GlobalSettingsConfig.ready(), so it runs in every process
that calls django.setup() — management commands, shell, Celery, WSGI/ASGI —
not only when the URLconf happens to be imported.
"""
import logging

from wagtail_transfer.models import get_base_model
from wagtail_transfer.operations import Objective

logger = logging.getLogger(__name__)

# The patched signature mirrors Objective.__init__ in this exact release. If the
# pin in requirements/base.txt moves, re-verify the signature and whether the
# upstream bug is fixed before trusting this patch.
EXPECTED_WAGTAIL_TRANSFER_VERSION = '0.11'

_PATCH_FLAG = '_openstax_base_model_patch'


def _patched_init(self, model, source_id, context, must_update=False):
    _original_init = _patched_init._original
    _original_init(self, get_base_model(model), source_id, context, must_update)


def apply_patches():
    """Install the Objective base-model normalization patch. Idempotent."""
    try:
        import importlib.metadata as _md
        installed = _md.version('wagtail-transfer')
    except Exception:  # pragma: no cover - metadata always present in practice
        installed = None
    if installed and installed != EXPECTED_WAGTAIL_TRANSFER_VERSION:
        logger.warning(
            "wagtail-transfer is %s but the Objective base-model patch was written "
            "for %s. Re-verify openstax/wagtail_transfer_patches.py.",
            installed, EXPECTED_WAGTAIL_TRANSFER_VERSION,
        )

    if getattr(Objective.__init__, _PATCH_FLAG, False):
        return  # already patched

    _patched_init._original = Objective.__init__
    setattr(_patched_init, _PATCH_FLAG, True)
    Objective.__init__ = _patched_init
