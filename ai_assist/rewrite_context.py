"""Describe where a piece of rich text lives, so a rewrite can suit its place.

The editor sends the page it is editing and the label of the field; everything
else comes from the saved page. Unsaved edits are therefore invisible here —
acceptable, because this is tone context, not source material.
"""

from django.utils.html import strip_tags
from wagtail.blocks.list_block import ListValue
from wagtail.blocks.stream_block import StreamValue
from wagtail.blocks.struct_block import StructValue
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.rich_text import RichText

NEIGHBOUR_CHARS = 1200


def _plain_text(value, out):
    if len(" ".join(out)) > NEIGHBOUR_CHARS:
        return
    if isinstance(value, RichText):
        out.append(strip_tags(value.source))
    elif isinstance(value, str):
        out.append(strip_tags(value))
    elif isinstance(value, StreamValue):
        for child in value:
            _plain_text(child.value, out)
    elif isinstance(value, (StructValue, dict)):
        for child in value.values():
            _plain_text(child, out)
    elif isinstance(value, (ListValue, list, tuple)):
        for child in value:
            _plain_text(child, out)


def neighbouring_text(page):
    out = []
    for field in page._meta.get_fields():
        if isinstance(field, (StreamField, RichTextField)):
            _plain_text(getattr(page, field.name, None), out)
    text = " ".join(part.strip() for part in out if part and part.strip())
    return text[:NEIGHBOUR_CHARS]


def build_brief(page_id=None, field_label=None):
    """One paragraph telling the model what it is rewriting and where it sits."""
    page = None
    if page_id:
        page = Page.objects.filter(pk=page_id).first()
        page = page.specific if page else None

    if page is None:
        return "You do not know which page this text belongs to."

    where = f'This text is on the page "{page.title}", a {page._meta.verbose_name}'
    if field_label:
        where += f', in the "{field_label}" field'
    lines = [where + "."]

    neighbours = neighbouring_text(page)
    if neighbours:
        lines.append(
            "The rest of the page reads like this — match it, and do not repeat "
            f"it: {neighbours}"
        )
    return "\n\n".join(lines)
