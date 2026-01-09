from django import template
from wagtail.fields import StreamField, RichTextField
from django.db.models import CharField, TextField

register = template.Library()

def extract_content(value):
    """
    Recursively extract text content from various Wagtail/Django field values.

    This helper is used to normalize content from complex structures such as
    StreamField and StructBlock values into a plain text string.

    Args:
        value:
            The value to extract text from. This can be:
            - Primitive types such as ``str``, ``int``, or ``float``.
            - Wagtail RichText-like objects (anything with a ``.source`` attribute).
            - Iterable values representing StreamField data (e.g. ``StreamValue``,
              ``ListValue`` or plain lists/tuples). Items that look like
              StreamField children (having ``value`` and ``block_type`` attributes)
              are unwrapped via their ``.value`` attribute.
            - Struct-like values (e.g. Wagtail's ``StructValue``) or plain Python
              ``dict`` objects, which are processed by extracting their values
              via the ``.values()`` method and recursively extracting content
              from each value.
            - ``None``, which is treated as empty content.

    Returns:
        str: A string containing the concatenated text content extracted from
        ``value`` and any nested structures. Returns an empty string if no
        textual content is found.

    Example:
        >>> extract_content("Title")
        'Title'
        >>> extract_content(None)
        ''
        >>> extract_content([{"foo": "bar"}, "baz"])
        'bar\nbaz'

    Edge cases:
        - Empty iterables or structures yield an empty string.
        - Unknown object types are converted to text with ``str(value)``.
    """
    if value is None:
        return ""

    if isinstance(value, (str, int, float)):
        return str(value)

    # RichText objects
    if hasattr(value, 'source'):
        return value.source

    # Handle StructValue and plain dicts before checking for general iterables.
    # This ensures dict-like objects are processed via their values() method
    # rather than being treated as iterable key sequences.
    # Note: Both Wagtail's StructValue and Python's dict have a values() method.
    if isinstance(value, dict) or (hasattr(value, 'values') and callable(getattr(value, 'values', None))):
        parts = []
        for v in value.values():
            parts.append(extract_content(v))
        return "\n".join(filter(None, parts))

    # Handle StreamValue / ListValue (lists, tuples, and other iterables)
    # We've already handled dicts above, and we exclude str/bytes here.
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        parts = []
        for item in value:
            # If it's a StreamChild (has 'value' and 'block_type'), use .value
            if hasattr(item, 'value') and hasattr(item, 'block_type'):
                parts.append(extract_content(item.value))
            else:
                parts.append(extract_content(item))
        return "\n".join(filter(None, parts))

    return str(value)

@register.simple_tag(takes_context=True)
def get_page_content(context, page):
    """
    Returns a list of renderable content chunks from the page's fields.
    Checks for StreamField, RichTextField, CharField, and TextField.
    """
    if not page:
        return []

    # Access the specific subclass instance to get all defined fields
    specific_page = page.specific
    content_items = []

    # Get all fields from the model
    fields = specific_page._meta.get_fields()

    for field in fields:
        # Skip internal/relation fields usually not content (simple heuristic)
        if field.name in ['id', 'path', 'depth', 'numchild', 'live', 'has_unpublished_changes',
                          'first_published_at', 'last_published_at', 'go_live_at', 'expire_at',
                          'content_type', 'owner', 'seo_title', 'search_description', 'slug', 'title',
                          'locked', 'locked_at', 'locked_by', 'latest_revision_created_at',
                          'live_revision', 'url_path', 'content_type_id', 'owner_id',
                          'locked_by_id', 'live_revision_id', 'generic_comments', 'wagtail_admin_comments']:
            continue
        
        # Check field types we want to render
        is_content_field = isinstance(field, (StreamField, RichTextField, CharField, TextField))
        
        if is_content_field:
            try:
                value = getattr(specific_page, field.name)
                if value:
                    try:
                        # Extract text content recursively
                        extracted_text = extract_content(value)
                        
                        # Determine type for template rendering
                        # Treat StreamField as RichTextField because extract_content returns raw HTML for RichBlocks
                        if isinstance(field, (RichTextField, StreamField)):
                            item_type = 'RichTextField'
                        else:
                            item_type = 'Text'

                        if extracted_text.strip():
                            content_items.append({
                                'name': field.name,
                                'value': extracted_text,
                                'type': item_type
                            })
                    except (TypeError, ValueError) as e:
                        print(f"Error extracting content from field {field.name}: {e}")
            except AttributeError:
                pass

    return content_items

