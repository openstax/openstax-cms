# authoring/migration.py
"""Turn a live FlexPage into a sanitized, import-ready payload.

Cross-environment object references (images, documents, snippet choosers, page
links) cannot survive a move between environments, so we blank them while keeping
the surrounding block/text/structure. The walk is driven by the real block
definitions (same source-of-truth principle as authoring/drafts.py), so we never
hardcode a fragile field-name list.

Assumption: source and target environments share the same FlexPage block schema.
Unknown block types are passed through unsanitized (their references would NOT be
blanked), so this tool is intended for environments running the same deployed code —
which is the case for dev/staging/prod of the same release.
"""
import re
from collections.abc import Sequence

from wagtail import blocks
from wagtail.blocks import ChooserBlock
from pages.models import FlexPage

# Mirror the rich-text tag patterns used in authoring/drafts.py, but for removal.
_PAGE_LINK_RE = re.compile(r'<a\b[^>]*\blinktype="page"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
_IMAGE_EMBED_RE = re.compile(r'<embed\b[^>]*\bembedtype="image"[^>]*/?>', re.IGNORECASE)


def _strip_richtext_refs(html):
    """Unwrap page links to their inner text; remove image embeds."""
    if not isinstance(html, str):
        return html
    html = _PAGE_LINK_RE.sub(r'\1', html)
    html = _IMAGE_EMBED_RE.sub('', html)
    return html


def sanitize_block(block, raw_value):
    """Recursively blank cross-env references in a stored-shape block value."""
    if isinstance(block, ChooserBlock):
        return None
    if isinstance(block, (blocks.RichTextBlock, blocks.RawHTMLBlock)):
        return _strip_richtext_refs(raw_value)
    if isinstance(block, blocks.StructBlock):
        if not isinstance(raw_value, dict):
            return raw_value
        sanitized = {
            name: sanitize_block(child, raw_value[name])
            for name, child in block.child_blocks.items()
            if name in raw_value
        }
        return {**raw_value, **sanitized}  # unknown keys pass through; known keys sanitized
    if isinstance(block, blocks.StreamBlock):
        return sanitize_raw_stream(block, raw_value)
    if isinstance(block, blocks.ListBlock):
        if isinstance(raw_value, str) or not isinstance(raw_value, Sequence):
            return raw_value
        out = []
        for item in raw_value:
            if isinstance(item, dict) and "value" in item:  # new list format
                out.append({**item, "value": sanitize_block(block.child_block, item["value"])})
            else:                                            # legacy bare-value format
                out.append(sanitize_block(block.child_block, item))
        return out
    return raw_value


def sanitize_raw_stream(stream_block, raw_data):
    """Sanitize a StreamField's raw list of {type, value, id} children.

    Accepts any non-string sequence (list, Wagtail's RawDataView, etc.) so
    callers can pass `page.body.raw_data` directly without converting it.
    """
    if isinstance(raw_data, str) or not isinstance(raw_data, Sequence):
        return raw_data
    out = []
    for node in raw_data:
        child = stream_block.child_blocks.get(node.get("type"))
        if child is None:
            out.append(node)  # unknown type: leave for the importer to reject
            continue
        out.append({**node, "value": sanitize_block(child, node.get("value"))})
    return out


def build_export_payload(page):
    """Live `title`/`slug`/`layout`/`body`, sanitized and import-shaped.

    Reads the LIVE field values (not the latest draft revision). `raw_data` is the
    stored {type, value, id} stream shape, which the import endpoint can ingest;
    the public api_fields representation is rendered/serialized and is NOT
    re-importable.
    """
    layout_block = FlexPage._meta.get_field("layout").stream_block
    body_block = FlexPage._meta.get_field("body").stream_block
    return {
        "title": page.title,
        "slug": page.slug,
        "layout": sanitize_raw_stream(layout_block, page.layout.raw_data),
        "body": sanitize_raw_stream(body_block, page.body.raw_data),
    }
