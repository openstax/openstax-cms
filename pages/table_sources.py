"""Resolvers that turn a dynamic table data-source spec into renderer-shaped
{columns, rows}. Output cells match the manual TableCellBlock API shape
({'content': html, 'cta': [CTALink dict]}), so the flex renderer consumes
manual and dynamic tables identically. All access is read-only."""

import json
import re
from types import SimpleNamespace
from urllib.parse import quote, urlsplit

from django.utils.html import escape, format_html
from wagtail.rich_text import expand_db_html

from books.constants import REMEDIATION_STATUSES, REMEDIATION_OUTSTANDING

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
            # Link getters may opt into extra CTA config (e.g. resource_ref
            # markers); everyone else gets the same [] as before.
            'config': raw.get('config') or [],
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
    'remediation_status': ('Remediation status',
                           lambda b: b.get_remediation_status_display() if b.remediation_status else '', 'text'),
}

DEFAULT_ROW_CAP = 100


def resolve_books(config):
    from django.db.models import Exists, OuterRef, Q
    from books.models import Book, BookFacultyResources, BookStudentResources
    qs = Book.objects.live().exclude(book_state__in=['unlisted', 'retired'])
    if config.get('book_state'):
        qs = qs.filter(book_state=config['book_state'])
    if config.get('subject'):
        qs = qs.filter(book_subjects__subject=config['subject'])
    remediation = config.get('remediation')
    if remediation in ('clear', 'outstanding'):
        # EXISTS subqueries instead of annotate(Count(...)) across two reverse
        # relations at once — combining two Counts like that fans out rows via
        # the join and double-counts (classic Django multi-annotation bug).
        # This stays one query regardless of how many resources a book has.
        outstanding_resource = Q(Exists(BookFacultyResources.objects.filter(
                                      book_faculty_resource=OuterRef('pk'),
                                      remediation_status__in=REMEDIATION_OUTSTANDING))) | \
                                Q(Exists(BookStudentResources.objects.filter(
                                      book_student_resource=OuterRef('pk'),
                                      remediation_status__in=REMEDIATION_OUTSTANDING)))
        has_outstanding = Q(remediation_status__in=REMEDIATION_OUTSTANDING) | outstanding_resource
        if remediation == 'outstanding':
            qs = qs.filter(has_outstanding)
        else:  # clear: nothing outstanding, but at least one tracked status somewhere
            tracked_resource = Q(Exists(BookFacultyResources.objects.filter(
                                      book_faculty_resource=OuterRef('pk')).exclude(remediation_status=''))) | \
                                Q(Exists(BookStudentResources.objects.filter(
                                      book_student_resource=OuterRef('pk')).exclude(remediation_status='')))
            has_tracked = ~Q(remediation_status='') | tracked_resource
            qs = qs.exclude(has_outstanding).filter(has_tracked)
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


# The book detail page selects its tab from a bare query-string key matching the
# tab label (os-webview findSelectedTab reads URLSearchParams keys), so
# ?Instructor%20resources opens that tab.
_BOOK_TABS = {'Student': 'Student resources', 'Videos': 'Videos'}


def _add_book(row, book):
    """Record a book on a (possibly shared) row. Titles gate the append so
    _book_slugs stays index-aligned with _book_titles."""
    if book.title not in row._book_titles:
        row._book_titles.append(book.title)
        row._book_slugs.append(book.slug)
        row._book_ids.append(book.pk)


def _book_page_link(r):
    """Book detail page URL, on the tab this row's resource lives under."""
    slug = next(iter(getattr(r, '_book_slugs', [])), '')
    if not slug:
        return ''
    tab = _BOOK_TABS.get(getattr(r, '_resource_type', ''), 'Instructor resources')
    return f'/details/books/{slug}?{quote(tab)}'


def _resource_link_cell(r):
    """The redaction books/serializers.py does per-request (blank the link
    unless ?x=y and the resource is unlocked) can't run here: this table's
    get_api_representation has no request/user and its output is cached and
    served to every visitor for up to 30 days.

    So a locked (or FK-null, SET_NULL) resource never gets its real file URL
    baked into public JSON. It points at the book detail page instead, where the
    existing resource box applies the normal gate with a working post-login
    return path — something we can't build here, since one cached cell is served
    to every reader and has no per-visitor "where you came from"."""
    if not (r.resource and r.resource.unlocked_resource):
        url = _book_page_link(r)
        if not url:
            return {'text': '', 'url': ''}
        # Marker for os-webview's progressive-enhancement override: it resolves
        # the real per-user link client-side (where verified-instructor status
        # is visible) and matches this cell back to a resource by heading.
        # book_slug is computed the same way as the fallback url above, so the
        # two can never drift apart.
        return {
            'text': 'View on book page',
            'url': url,
            'config': [{
                'type': 'resource_ref',
                'value': {
                    'book_slug': next(iter(getattr(r, '_book_slugs', [])), ''),
                    # trackLink() needs the numeric book id to post a
                    # download-tracking record; it is absent from the
                    # books/resources/ payload, so it has to ride along here.
                    'book_id': next(iter(getattr(r, '_book_ids', [])), None),
                    'heading': r.resource_heading if r.resource else '',
                    'resource_type': getattr(r, '_resource_type', ''),
                },
            }],
        }
    return {'text': r.link_text or 'View resource', 'url': _resource_link(r)}


RESOURCE_FIELDS = {
    'book': ('Book(s)', lambda r: ', '.join(getattr(r, '_book_titles', [])), 'text'),
    'heading': ('Resource', lambda r: r.resource_heading if r.resource else '', 'text'),
    # Expanded like the normal resource API (books.models uses ExpandedRichTextField)
    # so internal links resolve and the renderer paints it as HTML, not raw tags.
    'description': ('Description',
                    lambda r: expand_db_html(r.resource_description or '') if r.resource else '', 'html'),
    'link': ('Link', _resource_link_cell, 'link'),
    'coming_soon': ('Coming soon', lambda r: r.coming_soon_text or '', 'text'),
    'k12': ('K12', lambda r: 'Yes' if r.display_on_k12 else '', 'text'),
    'unlocked': ('Unlocked',
                 lambda r: 'Yes' if (r.resource and r.resource.unlocked_resource) else '', 'text'),
'resource_category': ('Category',
                      lambda r: (r.resource.resource_category or '') if r.resource else '', 'text'),
    'remediation_status': ('Remediation status',
                           lambda r: r.get_remediation_status_display() if r.remediation_status else '', 'text'),
    # Set by resolve_book_resources on each row (real or synthetic) — it knows
    # which manager/kind a row came from; the getter just reads it back.
    'resource_type': ('Resource type', lambda r: getattr(r, '_resource_type', ''), 'text'),
}


class _WebPDFRow:
    """Synthetic RESOURCE_FIELDS row for a book's own Web PDF (Book.remediation_status),
    not an ancillary resource. Exposes exactly the attributes the RESOURCE_FIELDS
    getters touch, so it renders like a real row without faking a full model instance."""
    # unlocked_resource=True (not the SimpleNamespace/model default) — a book's
    # Web PDF is public content, not an access-gated ancillary; explicit here
    # so _resource_link_cell's fail-closed check doesn't wrongly gate it.
    resource = SimpleNamespace(unlocked_resource=True, resource_category='')
    resource_heading = 'Web PDF'
    resource_description = ''
    link_text = ''
    link_external = ''
    link_document = None
    link_page = None
    coming_soon_text = ''
    display_on_k12 = False
    _resource_type = 'Book'

    def __init__(self, book):
        self.remediation_status = book.remediation_status
        self._book_titles = [book.title]
        self._book_slugs = [book.slug]
        self._book_ids = [book.pk]

    def get_remediation_status_display(self):
        return dict(REMEDIATION_STATUSES).get(self.remediation_status, '')


class _VideoResourceRow:
    """Wraps a books.models.VideoFacultyResources row for RESOURCE_FIELDS.
    VideoFacultyResource has no `resource` FK at all — video ancillaries are
    public, never access-gated — and no link_external/link_document/
    link_page/coming_soon_text/display_on_k12 fields. Expose exactly the
    attributes the RESOURCE_FIELDS getters touch, same approach as
    _WebPDFRow above, so _resource_link_cell's fail-closed check doesn't
    wrongly gate a public video row into a login prompt. The real
    video_url/video_file link rides in as link_external so _resource_link
    picks it up unmodified; with neither set, it degrades to a textual
    "no real link" cell exactly like a Web PDF row with no link, rather
    than inventing one."""
    resource = SimpleNamespace(unlocked_resource=True, resource_category='')
    link_document = None
    link_page = None
    coming_soon_text = ''
    display_on_k12 = False
    _resource_type = 'Videos'

    def __init__(self, video):
        self.resource_heading = video.resource_heading
        self.resource_description = video.resource_description
        self.remediation_status = video.remediation_status
        self.link_text = video.video_title or ''
        self.link_external = video.video_url or (video.video_file.url if video.video_file else '')
        self._get_display = video.get_remediation_status_display
        self._book_titles = []
        self._book_slugs = []
        self._book_ids = []

    def get_remediation_status_display(self):
        return self._get_display()


def _resource_books(config):
    """Books whose resources fill the table. Explicit picks win; otherwise all
    listed books, narrowed by HE subject and/or K12 subject area if set."""
    manual = [b.specific for b in (config.get('books') or []) if b]
    if manual:
        return manual
    from books.models import Book
    qs = Book.objects.live().exclude(book_state__in=['unlisted', 'retired'])
    if config.get('subject'):
        qs = qs.filter(book_subjects__subject=config['subject'])
    if config.get('k12_subject'):
        qs = qs.filter(k12book_subjects__subject=config['k12_subject'])
    return list(qs.distinct().order_by('title'))


def _keep_remediation(status, remediation):
    """remediation filter shared by real and synthetic (Web PDF) rows."""
    if not remediation:
        return True
    if remediation == 'outstanding':
        return status in REMEDIATION_OUTSTANDING
    if remediation == 'tracked':
        return bool(status)
    return status == remediation


def resolve_book_resources(config):
    books = _resource_books(config)
    if not books:
        return {'columns': [], 'rows': []}
    resource_type = config.get('resource_type') or 'instructor'
    # label used in both the dedup key (below) and the resource_type cell.
    managers = []
    if resource_type in ('instructor', 'all'):
        managers.append(('Instructor', 'book_faculty_resources'))
    if resource_type in ('student', 'all'):
        managers.append(('Student', 'book_student_resources'))
    include_video = resource_type in ('video', 'all')
    k12_only = config.get('audience') == 'k12'
    category = (config.get('resource_category') or '').strip()
    remediation = (config.get('remediation') or '').strip()
    include_web_pdf = bool(config.get('include_web_pdf'))
    # A resource snippet can be attached to several books; each distinct
    # (resource, link) pair gets one row, listing every book sharing it in
    # the "Book(s)" cell. See the key comment below for why link identity
    # is part of the key, not just the snippet id.
    deduped, order = {}, []
    for book in books:
        if include_web_pdf and _keep_remediation(book.remediation_status, remediation):
            key = ('web_pdf', book.pk)  # one per book — never collides with resource keys
            deduped[key] = _WebPDFRow(book)
            order.append(key)
        # Videos are a separate model (no `resource` FK, no resource_category,
        # no display_on_k12) — a category filter or K12-only view can never
        # match one, so skip the pool entirely rather than letting an
        # attribute lookup on those filters fail.
        if include_video and not category and not k12_only:
            for v in book.book_video_faculty_resources.all():
                if not _keep_remediation(v.remediation_status, remediation):
                    continue
                key = ('video', v.pk)  # one per book — a video row is never shared across books
                if key not in deduped:
                    deduped[key] = _VideoResourceRow(v)
                    order.append(key)
                _add_book(deduped[key], book)
        for label, manager_attr in managers:
            manager = getattr(book, manager_attr)
            # Getters touch resource/link_page/link_document per row — pull them in
            # one query each rather than N+1 (multiplied now across several books).
            resources = manager.select_related('resource', 'link_page', 'link_document')
            if category:
                resources = resources.filter(resource__resource_category=category)
            for r in resources:
                if k12_only and not r.display_on_k12:
                    continue
                if not _keep_remediation(r.remediation_status, remediation):
                    continue
                # Two books' resource rows merge into one table row only when they
                # share both the resource heading AND resolve to the same file —
                # sharing just the heading (e.g. "PowerPoint Slides") is common
                # and each book's copy is usually a distinct file (see spec).
                # Instructor/student are separate snippet models reusing the same
                # id sequence, so label is part of the key or "all" would collide them.
                key = ((label, r.resource_id, r.link_document_id, r.link_page_id, r.link_external)
                       if r.resource_id else (label, id(r)))
                if key not in deduped:
                    r._book_titles = []
                    r._book_slugs = []
                    r._book_ids = []
                    r._resource_type = label
                    deduped[key] = r
                    order.append(key)
                _add_book(deduped[key], book)
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
