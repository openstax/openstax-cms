# pages/flex_drafts.py
"""Pure (no-HTTP) helpers to validate and assemble FlexPage drafts.

Validation runs incoming JSON through the *actual* FlexPage StreamField block
definitions, so error messages match what a Wagtail editor would see. This makes
the CMS block definitions the single source of truth.
"""
from wagtail.blocks import StreamBlockValidationError

from pages.models import FlexPage

VALID_LAYOUT_TYPES = {"default", "landing"}


class FlexValidationError(Exception):
    """Carries a structured, agent-correctable error payload."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


def _stream_block(field_name):
    return FlexPage._meta.get_field(field_name).stream_block


def _clean(field_name, data):
    """Build a StreamValue from stored-shape data and clean it. Returns the
    cleaned StreamValue or raises FlexValidationError with per-block messages."""
    block = _stream_block(field_name)
    known = set(block.child_blocks.keys())
    unknown = [n.get("type") for n in data if n.get("type") not in known]
    if unknown:
        raise FlexValidationError({
            field_name: f"Unknown block type(s): {unknown}. Allowed: {sorted(known)}."
        })
    value = block.to_python(data)
    try:
        return block.clean(value)
    except StreamBlockValidationError as exc:
        raise FlexValidationError({field_name: _render_stream_errors(exc)})


def _render_stream_errors(exc):
    """Flatten a StreamBlockValidationError into a JSON-serialisable dict."""
    out = {}
    for idx, err in (getattr(exc, "block_errors", {}) or {}).items():
        out[idx] = [str(m) for m in getattr(err, "messages", [str(err)])]
    if getattr(exc, "non_block_errors", None):
        out["_"] = [str(m) for m in exc.non_block_errors]
    return out or {"_": [str(exc)]}


def validate_layout(data):
    """`layout` is REQUIRED and must be exactly one 'default' or 'landing' block."""
    if not data:
        raise FlexValidationError({"layout": "layout is required: provide exactly one "
                                              "'default' (site nav) or 'landing' block."})
    if len(data) != 1 or data[0].get("type") not in VALID_LAYOUT_TYPES:
        raise FlexValidationError({"layout": "layout must be exactly one of "
                                             f"{sorted(VALID_LAYOUT_TYPES)}."})
    return _clean("layout", data)


def validate_body(data):
    return _clean("body", data)


def create_flex_draft(*, parent, title, slug, layout_data, body_data, user=None):
    """Create a FlexPage under `parent` as an UNPUBLISHED draft revision.

    Never publishes. Returns (page, warnings). Caller is responsible for routing
    validation (slug already adjusted) before calling this.
    """
    validate_layout(layout_data)
    validate_body(body_data)

    page = FlexPage(
        title=title,
        slug=slug,
        layout=layout_data,
        body=body_data,
        live=False,
        has_unpublished_changes=True,
    )
    parent.add_child(instance=page)      # saves the page row (live=False)
    page.save_revision(user=user)        # creates the draft revision; does NOT publish
    return page, []


def update_flex_draft(*, page, title=None, layout_data=None, body_data=None, user=None):
    """Apply changes to an existing FlexPage as a NEW draft revision.

    Mutates only the in-memory instance + saves a revision; the live DB row's
    published fields are left intact until a human publishes. Returns (page, warnings).
    """
    if title is not None:
        page.title = title
    if layout_data is not None:
        validate_layout(layout_data)
        page.layout = layout_data
    if body_data is not None:
        validate_body(body_data)
        page.body = body_data

    page.save_revision(user=user)          # draft only; not published
    # Reflect unpublished changes without touching published fields.
    type(page).objects.filter(pk=page.pk).update(has_unpublished_changes=True)
    return page, []
