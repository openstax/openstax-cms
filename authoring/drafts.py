# authoring/drafts.py
"""Pure (no-HTTP) helpers to validate and assemble FlexPage drafts.

Validation runs incoming JSON through the *actual* FlexPage StreamField block
definitions, so error messages match what a Wagtail editor would see. This makes
the CMS block definitions the single source of truth.
"""
import re

from wagtail.blocks import StreamBlockValidationError
from wagtail.models import Page
from wagtail.images import get_image_model

from pages.models import FlexPage

VALID_LAYOUT_TYPES = {"default", "landing"}


class FlexValidationError(Exception):
    """Carries a structured, agent-correctable error payload."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


class PageLockedError(Exception):
    """Raised when attempting to write a page locked by another user."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)


_A_TAG_RE = re.compile(r'<a\b[^>]*>', re.IGNORECASE)
_EMBED_TAG_RE = re.compile(r'<embed\b[^>]*>', re.IGNORECASE)
_ID_RE = re.compile(r'\bid="(\d+)"')


def _iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_strings(v)


def _collect_reference_ids(data):
    """Walk raw string values (avoids JSON-escaping issues) and pull page/image ids
    from Wagtail rich-text link/embed tags."""
    page_ids, image_ids = set(), set()
    for s in _iter_strings(data):
        if 'linktype="page"' in s:
            for tag in _A_TAG_RE.findall(s):
                if 'linktype="page"' in tag:
                    m = _ID_RE.search(tag)
                    if m:
                        page_ids.add(int(m.group(1)))
        if 'embedtype="image"' in s:
            for tag in _EMBED_TAG_RE.findall(s):
                if 'embedtype="image"' in tag:
                    m = _ID_RE.search(tag)
                    if m:
                        image_ids.add(int(m.group(1)))
    return page_ids, image_ids


def validate_rich_text_references(data):
    """Reject rich-text page-links / image-embeds whose target id doesn't exist."""
    page_ids, image_ids = _collect_reference_ids(data)
    missing = {}
    if page_ids:
        existing = set(Page.objects.filter(id__in=page_ids).values_list("id", flat=True))
        bad = sorted(page_ids - existing)
        if bad:
            missing["page"] = bad
    if image_ids:
        existing = set(get_image_model().objects.filter(id__in=image_ids).values_list("id", flat=True))
        bad = sorted(image_ids - existing)
        if bad:
            missing["image"] = bad
    if missing:
        raise FlexValidationError({
            "references": {
                "message": "Rich-text references point to objects that don't exist. "
                           "Look up valid IDs via image/page search before writing.",
                "missing": missing,
            }
        })


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
    # An empty body is allowed for drafts (content can be filled in
    # incrementally); only validate block shapes when blocks are present.
    if not data:
        return _stream_block("body").to_python([])
    return _clean("body", data)


def create_flex_draft(*, parent, title, slug, layout_data, body_data, user=None):
    """Create a FlexPage under `parent` as an UNPUBLISHED draft revision.

    Never publishes. Returns (page, warnings). Caller is responsible for routing
    validation (slug already adjusted) before calling this.
    """
    validate_layout(layout_data)
    validate_body(body_data)
    validate_rich_text_references(body_data)

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
    if page.locked:
        raise PageLockedError(f"Page {page.id} is locked by another user and cannot be edited.")
    # validate everything before mutating anything
    if layout_data is not None:
        validate_layout(layout_data)
    if body_data is not None:
        validate_body(body_data)
        validate_rich_text_references(body_data)
    # apply
    if title is not None:
        page.title = title
    if layout_data is not None:
        page.layout = layout_data
    if body_data is not None:
        page.body = body_data

    page.save_revision(user=user)          # draft only; not published
    # Reflect unpublished changes without touching published fields.
    type(page).objects.filter(pk=page.pk).update(has_unpublished_changes=True)
    return page, []
