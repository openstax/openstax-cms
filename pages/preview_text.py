"""Plain-text extraction for headless preview content metrics.

Wagtail's content-metrics panel (Words / Reading time / Readability) reads the
`innerText` of a `main` element inside the preview iframe. Our headless preview
(`RootPage.serve_preview`) renders the real site in a nested iframe, so that
document has no readable text and the metrics show dashes.

To restore real metrics we extract the page's text here and render it into a
visually-hidden `<main>` in `preview.html` (see that template). We reuse
Wagtail's own `get_searchable_content`, so any StreamField block type that works
with search also works here, with no per-block maintenance.
"""

from django.db import models
from django.utils.html import strip_tags

from wagtail.fields import RichTextField, StreamField

# Core/SEO/meta fields that aren't part of the visible content body.
SKIP_FIELDS = {"slug", "seo_title", "search_description", "draft_title", "url_path"}


def stream_searchable_text(stream_value):
    """Return the searchable plain text of a StreamField value.

    Uses the StreamBlock's get_searchable_content (which recurses into nested
    struct/stream/list blocks), with a defensive per-block fallback.
    """
    if stream_value is None:
        return ""
    try:
        return " ".join(
            stream_value.stream_block.get_searchable_content(stream_value)
        )
    except Exception:
        parts = []
        try:
            for bound_block in stream_value:
                try:
                    parts.extend(
                        bound_block.block.get_searchable_content(bound_block.value)
                        or []
                    )
                except Exception:
                    continue
        except Exception:
            pass
        return " ".join(parts)


def extract_page_text(page):
    """Best-effort plain text of a page's editable content.

    Walks StreamField, RichTextField, and plain Char/Text fields, skipping
    SEO/meta fields. Defensive: a problematic field is skipped, never raised,
    so preview rendering can't break.
    """
    parts = []
    for field in page._meta.get_fields():
        attname = getattr(field, "attname", None)
        if not attname or field.name in SKIP_FIELDS:
            continue
        try:
            value = getattr(page, attname, None)
        except Exception:
            continue
        if value in (None, ""):
            continue
        if isinstance(field, StreamField):
            parts.append(stream_searchable_text(value))
        elif isinstance(field, RichTextField):
            parts.append(strip_tags(value))
        elif isinstance(field, (models.CharField, models.TextField)):
            parts.append(str(value))
    return "\n".join(p for p in parts if p and p.strip())
