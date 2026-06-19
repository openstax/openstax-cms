"""Shared DRF serializer fields and Wagtail block types for the OpenStax CMS API.

Kept dependency-free of app models so any app can import it without import
cycles.
"""
from bs4 import BeautifulSoup
from rest_framework import serializers
from wagtail import blocks
from wagtail.rich_text import expand_db_html


# Tags that make an otherwise-textless paragraph worth keeping.
_MEDIA_TAGS = ('img', 'picture', 'svg', 'iframe', 'video', 'audio', 'embed', 'object')


def strip_empty_paragraphs(html):
    """Remove blank paragraphs left by the rich text editor.

    Wagtail's editor serializes empty lines as ``<p></p>``, ``<p><br></p>``, or
    whitespace/``&nbsp;``-only paragraphs, which render as stray vertical gaps.
    Drop those, keeping any paragraph that carries media. Run once when a block
    is saved (see ``APIRichTextBlock.get_prep_value``) so the stored HTML is
    already clean and read paths pay nothing.
    """
    if not html:
        return html
    soup = BeautifulSoup(html, 'html.parser')
    for paragraph in soup.find_all('p'):
        if paragraph.find(_MEDIA_TAGS):
            continue
        # str.strip() also removes non-breaking spaces, so &nbsp;-only
        # paragraphs collapse to empty here too.
        if not paragraph.get_text().strip():
            paragraph.decompose()
    return str(soup)


class APIRichTextBlock(blocks.RichTextBlock):
    """RichTextBlock that drops blank paragraphs on save and expands internal
    page links in API output."""

    def get_prep_value(self, value):
        # Clean the source HTML once, as the block is serialized to the database,
        # rather than on every read.
        return strip_empty_paragraphs(super().get_prep_value(value))

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        return expand_db_html(representation)

    class Meta:
        icon = 'doc-full'


class ExpandedRichTextField(serializers.Field):
    """Serialize a model RichTextField with internal links/embeds expanded.

    DRF's default ``get_attribute`` reads ``instance.<source>`` (the field name
    set by ``APIField``) and passes that value here, so no ``get_attribute``
    override is needed. ``expand_db_html`` rewrites ``<a linktype="page" id=N>``
    into a real ``href`` via the page link handler (which uses ``page.url`` →
    each model's ``get_url_parts`` override → the frontend route).
    """

    def to_representation(self, value):
        return expand_db_html(value or "")
