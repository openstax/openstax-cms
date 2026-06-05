from django.db import models
from django.utils.html import strip_tags

from wagtail.fields import RichTextField, StreamField

SKIP_FIELDS = {"slug", "seo_title", "search_description", "draft_title", "url_path"}


def stream_searchable_text(stream_value):
    if stream_value is None:
        return ""
    try:
        return " ".join(stream_value.stream_block.get_searchable_content(stream_value))
    except Exception:
        parts = []
        try:
            for bound_block in stream_value:
                try:
                    parts.extend(
                        bound_block.block.get_searchable_content(bound_block.value) or []
                    )
                except Exception:
                    continue
        except Exception:
            pass
        return " ".join(parts)


def extract_page_text(page):
    """Plain text of a page's editable content, for the preview content-metrics panel."""
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
