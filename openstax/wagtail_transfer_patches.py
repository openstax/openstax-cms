"""
Runtime patches for wagtail-transfer 0.11.

Two patches, both installed by `apply_patches()`:

1. Objective base-model normalization. When importing pages, an Objective is
   occasionally constructed with a Page subclass (e.g. pages.RootPage) instead
   of the base wagtailcore.Page. The import context's uids_by_source /
   destination_ids_by_source dicts are keyed by base model, so the subclass
   lookup raises KeyError in Objective._find_at_destination (operations.py:
   `uids_by_source[(self.model, self.source_id)]`). Objective.__eq__/__hash__
   also key on self.model, so normalizing in __init__ additionally fixes
   set-dedup of objectives. Every other call site in wagtail-transfer normalizes
   via get_base_model() — this patch closes the one gap that leaks the subclass
   through. Upstream issue:
   https://github.com/wagtail/wagtail-transfer/issues/127 (open as of 0.11).

2. add_json error clarity. The import views (import_page / import_model /
   import_missing_object_data) pass the source's raw HTTP response body straight
   to ImportPlanner.add_json() without checking the status code. When the source
   returns anything but the expected JSON — a 403 (WAGTAILTRANSFER_SECRET_KEY
   mismatch), a 404 (page/object missing on the source, or a model rejected by
   our export allowlist), or — because this CMS is headless — the frontend SPA
   shell for a 404, add_json's json.loads() blows up with the opaque
   "Expecting value: line 1 column 1 (char 0)". This patch wraps add_json to
   re-raise that as a WagtailTransferImportError quoting the source's actual
   response, so the real cause is visible. It guards add_json (the shared
   chokepoint of all three import flows) rather than the view bodies, so the
   chooser proxy's deliberate status passthrough is untouched and we copy no
   upstream view logic that could drift when the pin moves.

`apply_patches()` is idempotent and is called from
global_settings.apps.GlobalSettingsConfig.ready(), so it runs in every process
that calls django.setup() — management commands, shell, Celery, WSGI/ASGI —
not only when the URLconf happens to be imported.
"""
import json
import logging

from wagtail_transfer.models import get_base_model
from wagtail_transfer.operations import ImportPlanner, Objective

logger = logging.getLogger(__name__)


class WagtailTransferImportError(Exception):
    """A wagtail-transfer source returned a non-JSON (HTTP error) response."""

# The patched signature mirrors Objective.__init__ in this exact release. If the
# pin in requirements/base.txt moves, re-verify the signature and whether the
# upstream bug is fixed before trusting this patch.
EXPECTED_WAGTAIL_TRANSFER_VERSION = '0.11'

_PATCH_FLAG = '_openstax_base_model_patch'
_ADD_JSON_PATCH_FLAG = '_openstax_add_json_guard'


def _patched_init(self, model, source_id, context, must_update=False):
    _original_init = _patched_init._original
    _original_init(self, get_base_model(model), source_id, context, must_update)


def _response_snippet(json_data, limit=300):
    """First `limit` chars of the source response, for the error message."""
    if isinstance(json_data, (bytes, bytearray)):
        text = json_data.decode('utf-8', errors='replace')
    else:
        text = str(json_data)
    return text.strip()[:limit]


def _patched_add_json(self, json_data):
    try:
        return _patched_add_json._original(self, json_data)
    except json.JSONDecodeError as exc:
        raise WagtailTransferImportError(
            "wagtail-transfer received a non-JSON response from the source site, "
            "so the import could not be read. The source almost certainly returned "
            "an HTTP error page instead of export data: a 403 (the source's "
            "WAGTAILTRANSFER_SECRET_KEY does not match the SECRET_KEY this "
            "environment has configured for it), a 404 (the page/object does not "
            "exist on the source, BASE_URL is wrong, or the model is not in the "
            "export allowlist), or this site's headless frontend shell. "
            f"Source response began with:\n{_response_snippet(json_data)}"
        ) from exc


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

    if not getattr(Objective.__init__, _PATCH_FLAG, False):
        _patched_init._original = Objective.__init__
        setattr(_patched_init, _PATCH_FLAG, True)
        Objective.__init__ = _patched_init

    if not getattr(ImportPlanner.add_json, _ADD_JSON_PATCH_FLAG, False):
        _patched_add_json._original = ImportPlanner.add_json
        setattr(_patched_add_json, _ADD_JSON_PATCH_FLAG, True)
        ImportPlanner.add_json = _patched_add_json
