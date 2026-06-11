"""Shared DRF serializer fields and Wagtail block types for the OpenStax CMS API.

Kept dependency-free of app models so any app can import it without import
cycles.
"""
from rest_framework import serializers
from wagtail import blocks
from wagtail.rich_text import expand_db_html


class APIRichTextBlock(blocks.RichTextBlock):
    """RichTextBlock that expands internal page links in API output."""

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
