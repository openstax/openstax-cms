"""Resolvers that turn a dynamic table data-source spec into renderer-shaped
{columns, rows}. Output cells match the manual TableCellBlock API shape
({'content': html, 'cta': [CTALink dict]}), so the flex renderer consumes
manual and dynamic tables identically. All access is read-only."""

import re

from django.utils.html import escape, format_html

_HAS_SCHEME = re.compile(r'^([a-z][a-z0-9+.-]*:|//)', re.IGNORECASE)

# Cell types authors can pick in source column mappings. 'html' is
# registry-internal (rich-text fields) and not offered as a choice.
SOURCE_CELL_TYPE_CHOICES = [
    ('text', 'Text'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('link', 'Link'),
    ('image', 'Image'),
]

RENDERER_COLUMN_TYPES = {'text', 'number', 'date'}


def _empty_cell():
    return {'content': '', 'cta': []}


def build_cell(raw, cell_type):
    if raw is None or raw == '':
        return _empty_cell()
    if cell_type == 'link':
        url = (raw.get('url') or '').strip()
        text = raw.get('text') or url
        if not url:
            return {'content': escape(str(text)) if text else '', 'cta': []}
        return {'content': '', 'cta': [{
            'text': str(text),
            'aria_label': '',
            'target': {
                'value': url,
                'type': 'external' if _HAS_SCHEME.match(url) else 'internal',
            },
            'config': [],
        }]}
    if cell_type == 'image':
        url = raw.get('url') if isinstance(raw, dict) else raw
        if not url:
            return _empty_cell()
        alt = raw.get('alt', '') if isinstance(raw, dict) else ''
        return {'content': format_html('<img src="{}" alt="{}">', url, alt), 'cta': []}
    if cell_type == 'date':
        text = raw.strftime('%m/%d/%Y') if hasattr(raw, 'strftime') else escape(str(raw))
        return {'content': text, 'cta': []}
    if cell_type == 'html':
        return {'content': str(raw), 'cta': []}
    # text / number
    return {'content': escape(str(raw)), 'cta': []}


def build_table(columns_config, registry, items):
    """columns_config: [{'field', 'header', 'type'}]; registry: field -> (label,
    getter, default_type); items: iterable of source objects."""
    columns, builders = [], []
    for col in columns_config:
        entry = registry.get(col['field'])
        if entry is None:
            continue  # field removed from the registry after the page was saved
        label, getter, default_type = entry
        cell_type = col.get('type') or default_type
        renderer_type = cell_type if cell_type in RENDERER_COLUMN_TYPES else 'text'
        columns.append({'header': col.get('header') or label, 'type': renderer_type})
        builders.append((getter, cell_type))
    rows = []
    for item in items:
        cells = []
        for getter, cell_type in builders:
            try:
                raw = getter(item)
            except Exception:
                raw = None
            cells.append(build_cell(raw, cell_type))
        rows.append({'cells': cells})
    return {'columns': columns, 'rows': rows}


def field_choices(registry):
    return [(key, label) for key, (label, _getter, _type) in registry.items()]


# --- Books source ---------------------------------------------------------
# Getters return raw values; link/image getters return the dict build_cell
# expects. Lambdas take a books.models.Book page.
BOOK_FIELDS = {
    'title': ('Title', lambda b: b.title, 'text'),
    'title_link': ('Title (linked to book page)',
                   lambda b: {'text': b.title, 'url': f'/details/books/{b.slug}'}, 'link'),
    'subjects': ('Subjects', lambda b: ', '.join(b.subjects()), 'text'),
    'publish_date': ('Publish date', lambda b: b.publish_date, 'date'),
    'book_state': ('State', lambda b: b.get_book_state_display(), 'text'),
    'cover': ('Cover image', lambda b: {'url': b.cover_url, 'alt': b.title}, 'image'),
    'is_ap': ('AP', lambda b: 'Yes' if b.is_ap else '', 'text'),
    'read_online': ('Read online (link)',
                    lambda b: {'text': 'Read online',
                               'url': b.webview_rex_link or b.webview_link}, 'link'),
}

DEFAULT_ROW_CAP = 100


def resolve_books(config):
    from books.models import Book
    qs = Book.objects.live().exclude(book_state__in=['unlisted', 'retired'])
    if config.get('book_state'):
        qs = qs.filter(book_state=config['book_state'])
    if config.get('subject'):
        qs = qs.filter(book_subjects__subject=config['subject'])
    qs = qs.order_by(config.get('order') or 'title')
    limit = config.get('limit') or DEFAULT_ROW_CAP
    return build_table(config['columns'], BOOK_FIELDS, qs.distinct()[:limit])
