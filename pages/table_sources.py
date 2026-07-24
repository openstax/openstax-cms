"""Resolvers that turn a dynamic table data-source spec into renderer-shaped
{columns, rows}. Output cells match the manual table's cell API shape
({'content': html, 'cta': [CTALink dict]}), so the flex renderer consumes
manual and dynamic tables identically. All access is read-only."""

import json
import re
from urllib.parse import urlsplit

from django.utils.html import escape, format_html
from wagtail.rich_text import expand_db_html

_HAS_SCHEME = re.compile(r'^([a-z][a-z0-9+.-]*:|//)', re.IGNORECASE)

# Schemes a link cell may carry into an href. Anything else with a scheme
# (javascript:, data:, file:, ...) degrades to a plain text cell — dynamic
# sources (endpoint JSON, snippet char fields) are not trusted URL input.
_SAFE_LINK_SCHEMES = {'http', 'https', 'mailto', 'tel'}

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
        if not isinstance(raw, dict):
            raw = {'url': str(raw), 'text': str(raw)}
        url = (raw.get('url') or '').strip()
        text = raw.get('text') or url
        scheme = urlsplit(url).scheme.lower()
        if not url or (scheme and scheme not in _SAFE_LINK_SCHEMES):
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
        requested = col.get('type')
        # Rich-text fields always render as HTML (never escaped); the column
        # type dropdown only picks their sort order. Everything else escapes.
        if default_type == 'html':
            cell_type = 'html'
            renderer_type = requested if requested in RENDERER_COLUMN_TYPES else 'text'
        else:
            cell_type = requested or default_type
            renderer_type = cell_type if cell_type in RENDERER_COLUMN_TYPES else 'text'
        columns.append({'header': col.get('header') or label, 'type': renderer_type})
        builders.append((getter, cell_type))
    rows = []
    for item in items:
        cells = []
        for getter, cell_type in builders:
            try:
                cell = build_cell(getter(item), cell_type)
            except Exception:
                cell = {'content': '', 'cta': []}
            cells.append(cell)
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


# --- Blog (news) source ----------------------------------------------------
NEWS_FIELDS = {
    'heading': ('Heading', lambda a: a.heading, 'text'),
    'heading_link': ('Heading (linked to article)',
                     lambda a: {'text': a.heading, 'url': f'/blog/{a.slug}'}, 'link'),
    'subheading': ('Subheading', lambda a: a.subheading, 'text'),
    'author': ('Author', lambda a: a.author, 'text'),
    'date': ('Post date', lambda a: a.date, 'date'),
    'image': ('Article image', lambda a: {'url': a.article_image, 'alt': a.heading}, 'image'),
}


def resolve_news(config):
    from news.models import NewsArticle
    qs = NewsArticle.objects.live().order_by(config.get('order') or '-date')
    if config.get('tag'):
        qs = qs.filter(tags__name__iexact=config['tag'])
    limit = config.get('limit') or 20
    subject = (config.get('subject') or '').strip().lower()
    if subject:
        # article_subjects stores Subject snippet IDs, so match against the
        # resolved subject names via the model's search_subject_names().
        # Iterate lazily and stop at limit so no arbitrary pre-cap can drop
        # later matches.
        articles = []
        for article in qs.iterator():
            if subject in article.search_subject_names().lower():
                articles.append(article)
                if len(articles) >= limit:
                    break
    else:
        articles = qs[:limit]
    return build_table(config['columns'], NEWS_FIELDS, articles)


# --- Book resources source --------------------------------------------------
def _resource_link(r):
    if r.link_external:
        return r.link_external
    if r.link_document:
        return r.link_document_url
    if r.link_page:
        page = r.link_page.specific
        return page.url or page.url_path
    return ''


RESOURCE_FIELDS = {
    'book': ('Book(s)', lambda r: ', '.join(getattr(r, '_book_titles', [])), 'text'),
    'heading': ('Resource', lambda r: r.resource_heading if r.resource else '', 'text'),
    # Expanded like the normal resource API (books.models uses ExpandedRichTextField)
    # so internal links resolve and the renderer paints it as HTML, not raw tags.
    'description': ('Description',
                    lambda r: expand_db_html(r.resource_description or '') if r.resource else '', 'html'),
    'link': ('Link', lambda r: {'text': r.link_text or 'View resource',
                                'url': _resource_link(r)}, 'link'),
    'coming_soon': ('Coming soon', lambda r: r.coming_soon_text or '', 'text'),
    'k12': ('K12', lambda r: 'Yes' if r.display_on_k12 else '', 'text'),
    'unlocked': ('Unlocked',
                 lambda r: 'Yes' if (r.resource and r.resource.unlocked_resource) else '', 'text'),
'resource_category': ('Category',
                      lambda r: (r.resource.resource_category or '') if r.resource else '', 'text'),
}


def resolve_book_resources(config):
    books = [b.specific for b in (config.get('books') or []) if b]
    if not books:
        return {'columns': [], 'rows': []}
    student = config.get('resource_type') == 'student'
    k12_only = config.get('audience') == 'k12'
    category = (config.get('resource_category') or '').strip()
    # A resource snippet can be attached to several books; each distinct
    # (resource, link) pair gets one row, listing every book sharing it in
    # the "Book(s)" cell. See the key comment below for why link identity
    # is part of the key, not just the snippet id.
    deduped, order = {}, []
    for book in books:
        manager = book.book_student_resources if student else book.book_faculty_resources
        # Getters touch resource/link_page/link_document per row — pull them in
        # one query each rather than N+1 (multiplied now across several books).
        resources = manager.select_related('resource', 'link_page', 'link_document')
        if category:
            resources = resources.filter(resource__resource_category=category)
        for r in resources:
            if k12_only and not r.display_on_k12:
                continue
            # Two books' resource rows merge into one table row only when they
            # share both the resource heading AND resolve to the same file —
            # sharing just the heading (e.g. "PowerPoint Slides") is common
            # and each book's copy is usually a distinct file (see spec).
            key = ((r.resource_id, r.link_document_id, r.link_page_id, r.link_external)
                   if r.resource_id else id(r))
            if key not in deduped:
                r._book_titles = []
                deduped[key] = r
                order.append(key)
            titles = deduped[key]._book_titles
            if book.title not in titles:
                titles.append(book.title)
    return build_table(config['columns'], RESOURCE_FIELDS, [deduped[k] for k in order])


# --- Subjects source (HE Subject + K12Subject snippets) ---------------------
SUBJECT_FIELDS = {
    'name': ('Subject', lambda s: s.name, 'text'),
    'category': ('Category', lambda s: getattr(s, 'subject_category', ''), 'text'),
    'color': ('Color', lambda s: s.subject_color, 'text'),
    'icon': ('Icon', lambda s: {
        'url': getattr(s, 'subject_icon', None) or getattr(s, 'subject_image', None),
        'alt': s.name}, 'image'),
    'link': ('Link (K12 subject pages)', lambda s: {
        'text': s.name, 'url': getattr(s, 'subject_link', '') or ''}, 'link'),
}


def resolve_subjects(config):
    from wagtail.models import Locale
    from snippets.models import Subject, K12Subject
    locale = Locale.get_default()
    if config.get('variant') == 'k12':
        qs = K12Subject.objects.filter(locale=locale).order_by('name')
        if config.get('k12_category'):
            qs = qs.filter(subject_category__iexact=config['k12_category'])
    else:
        qs = Subject.objects.filter(locale=locale).order_by('name')
    return build_table(config['columns'], SUBJECT_FIELDS, qs)


# --- Endpoint escape hatch ---------------------------------------------------
# Resolves a RELATIVE CMS API path in-process (no HTTP hop): RequestFactory +
# URL resolution, then generic dotted-path field mapping over the JSON items.
# Only /apps/cms/api/ paths are allowed — these are public-read endpoints, so
# calling them unauthenticated leaks nothing, and relative paths keep the spec
# portable across dev/staging/prod.
ENDPOINT_PREFIX = '/apps/cms/api/'


def _dig(obj, dotted):
    for part in dotted.split('.'):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def resolve_endpoint(config):
    from django.test import RequestFactory
    from django.urls import resolve as url_resolve

    path = (config.get('path') or '').strip()
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith(ENDPOINT_PREFIX):
        raise ValueError(f'Endpoint path must be relative and start with {ENDPOINT_PREFIX}')

    request = RequestFactory().get(path)
    try:
        match = url_resolve(parsed.path)
        response = match.func(request, *match.args, **match.kwargs)
        if hasattr(response, 'render'):
            response.render()
    except Exception as e:
        raise ValueError(f'Endpoint {parsed.path} could not be resolved: {e}') from e
    if response.status_code != 200:
        raise ValueError(f'Endpoint {parsed.path} returned {response.status_code}')
    payload = json.loads(response.content)

    items_key = config.get('items_key', 'items')
    if items_key:
        if not isinstance(payload, dict):
            raise ValueError('Endpoint response is not an object; clear the items key for bare-list responses')
        items = payload.get(items_key) or []
    else:
        items = payload
    if not isinstance(items, list):
        raise ValueError(f'Endpoint response key {items_key!r} is not a list')

    columns, rows = [], []
    for col in config['columns']:
        cell_type = col.get('type') or 'text'
        renderer_type = cell_type if cell_type in RENDERER_COLUMN_TYPES else 'text'
        columns.append({'header': col.get('header') or col['field'], 'type': renderer_type})
    for item in items:
        cells = []
        for col in config['columns']:
            raw = _dig(item, col['field'])
            cells.append(build_cell(raw, col.get('type') or 'text'))
        rows.append({'cells': cells})
    return {'columns': columns, 'rows': rows}


# --- Dispatcher --------------------------------------------------------------
def resolve_data_source(source_type, config):
    """Resolve one data_source stream child into {'columns', 'rows'}.
    Late-bound lookup (not a dict of function refs) so tests can patch the
    individual resolvers."""
    resolver = {
        'books': 'resolve_books',
        'news': 'resolve_news',
        'book_resources': 'resolve_book_resources',
        'subjects': 'resolve_subjects',
        'endpoint': 'resolve_endpoint',
    }[source_type]
    return globals()[resolver](config)
