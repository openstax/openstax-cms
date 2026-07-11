import hashlib
import json

from django.core.cache import cache
from sentry_sdk import capture_exception
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from openstax.api_fields import APIRichTextBlock
from pages.shared_blocks import CTALinkBlock, id_config_block
from pages.table_sources import (
    SOURCE_CELL_TYPE_CHOICES, field_choices,
    BOOK_FIELDS, NEWS_FIELDS, RESOURCE_FIELDS, SUBJECT_FIELDS,
)


# User-facing column sort types (renderer uses these to pick a comparator).
COLUMN_TYPE_CHOICES = [
    ('text', 'Text'),
    ('number', 'Number'),
    ('date', 'Date'),
]


def source_columns_block(choices):
    """Field → column mapping list shared by all dynamic source blocks."""
    return blocks.ListBlock(blocks.StructBlock([
        ('field', blocks.ChoiceBlock(choices=choices, required=True)),
        ('header', blocks.CharBlock(required=False,
            help_text='Column header shown to readers. Defaults to the field label.')),
        ('type', blocks.ChoiceBlock(choices=SOURCE_CELL_TYPE_CHOICES, required=False,
            help_text='Overrides how the value is shown and sorted. Default per field.')),
    ], label='Column'), min_num=1, label='Columns')


BOOK_STATE_CHOICES = [
    ('live', 'Live'),
    ('coming_soon', 'Coming Soon'),
    ('new_edition_available', 'New Edition Forthcoming'),
    ('deprecated', 'Deprecated'),
]


class BooksSourceBlock(blocks.StructBlock):
    subject = SnippetChooserBlock('snippets.Subject', required=False,
        help_text='Only books in this subject. Leave empty for all subjects.')
    book_state = blocks.ChoiceBlock(choices=BOOK_STATE_CHOICES, required=False,
        help_text='Only books in this state. Leave empty for all listed books.')
    order = blocks.ChoiceBlock(choices=[
        ('title', 'Title A–Z'),
        ('-publish_date', 'Newest first'),
        ('publish_date', 'Oldest first'),
    ], required=False, help_text='Row order. Default Title A–Z.')
    limit = blocks.IntegerBlock(required=False, min_value=1, max_value=500,
        help_text='Maximum number of rows. Default 100.')
    columns = source_columns_block(field_choices(BOOK_FIELDS))

    class Meta:
        label = 'Books'
        icon = 'doc-full'


class NewsSourceBlock(blocks.StructBlock):
    subject = blocks.CharBlock(required=False,
        help_text='Only articles with this subject, e.g. Science. Matches the article\'s subjects list.')
    tag = blocks.CharBlock(required=False,
        help_text='Only articles with this tag (exact tag name).')
    order = blocks.ChoiceBlock(choices=[
        ('-date', 'Newest first'),
        ('date', 'Oldest first'),
        ('heading', 'Heading A–Z'),
    ], required=False, help_text='Row order. Default newest first.')
    limit = blocks.IntegerBlock(required=False, min_value=1, max_value=500,
        help_text='Maximum number of rows. Default 20.')
    columns = source_columns_block(field_choices(NEWS_FIELDS))

    class Meta:
        label = 'Blog posts'
        icon = 'doc-empty'


def resource_category_choices():
    # Called each time the edit form renders, so the dropdown tracks whatever
    # categories editors have actually typed into the (free-text) snippet field.
    from snippets.models import FacultyResource, StudentResource
    categories = set()
    for model in (FacultyResource, StudentResource):
        categories.update(
            model.objects.exclude(resource_category__isnull=True)
            .exclude(resource_category__exact='')
            .values_list('resource_category', flat=True))
    return [(c, c) for c in sorted(categories)]


class BookResourcesSourceBlock(blocks.StructBlock):
    books = blocks.ListBlock(
        blocks.PageChooserBlock(page_type=['books.Book']),
        min_num=1, label='Books',
        help_text='The book(s) whose resources fill the table. A resource shared '
                  'across several books is listed once, with all its book names.')
    resource_type = blocks.ChoiceBlock(choices=[
        ('instructor', 'Instructor resources'),
        ('student', 'Student resources'),
    ], default='instructor')
    audience = blocks.ChoiceBlock(choices=[
        ('all', 'All'),
        ('k12', 'K12 only'),
    ], required=False,
        help_text='K12 only limits rows to resources flagged "Display on K12".')
    resource_category = blocks.ChoiceBlock(choices=resource_category_choices, required=False,
        help_text='Only resources with this category. Leave blank for all categories.')
    columns = source_columns_block(field_choices(RESOURCE_FIELDS))

    class Meta:
        label = 'Book resources'
        icon = 'clipboard-list'


class SubjectsSourceBlock(blocks.StructBlock):
    variant = blocks.ChoiceBlock(choices=[
        ('he', 'Higher Ed subjects'),
        ('k12', 'K12 subjects'),
    ], default='he')
    k12_category = blocks.CharBlock(required=False,
        help_text='K12 only: limit to a category, e.g. Math.')
    columns = source_columns_block(field_choices(SUBJECT_FIELDS))

    class Meta:
        label = 'Subjects'
        icon = 'tag'


class EndpointSourceBlock(blocks.StructBlock):
    path = blocks.RegexBlock(regex=r'^/apps/cms/api/\S*$',
        label='Endpoint path',
        help_text='Relative CMS API path including query string, e.g. '
                  '/apps/cms/api/v2/pages/?type=books.Book&fields=title,cover_url&book_state=live. '
                  'Must start with /apps/cms/api/. No absolute URLs — they break across environments.',
        error_messages={'invalid': 'Must be a relative path starting with /apps/cms/api/.'})
    items_key = blocks.CharBlock(required=False, default='items',
        help_text='JSON key holding the list of rows. Default "items" (the Wagtail API shape); clear it if the response is a bare list.')
    columns = blocks.ListBlock(blocks.StructBlock([
        ('field', blocks.CharBlock(required=True,
            help_text='Dotted path into each item, e.g. title or meta.slug.')),
        ('header', blocks.CharBlock(required=False,
            help_text='Column header. Defaults to the field path.')),
        ('type', blocks.ChoiceBlock(choices=SOURCE_CELL_TYPE_CHOICES, required=False,
            help_text='Cell type. Default text.')),
    ], label='Column'), min_num=1, label='Columns')

    class Meta:
        label = 'CMS API endpoint (advanced)'
        icon = 'code'


class TableCellBlock(blocks.StructBlock):
    content = APIRichTextBlock(required=False,
        help_text='Rich-text cell content. Ignored when a Call To Action is set.')
    cta = blocks.ListBlock(CTALinkBlock(required=False, label='Link'),
        default=[], max_num=1, label='Call To Action')

    class Meta:
        label = 'Cell'


class TableColumnBlock(blocks.StructBlock):
    header = blocks.CharBlock(required=True)
    type = blocks.ChoiceBlock(choices=COLUMN_TYPE_CHOICES, required=False,
        help_text='How readers sort this column. Default text.')

    class Meta:
        label = 'Column'


class TableRowBlock(blocks.StructBlock):
    cells = blocks.ListBlock(TableCellBlock(), default=[])

    class Meta:
        label = 'Row'


class TableBlock(blocks.StructBlock):
    caption = blocks.CharBlock(required=False,
        help_text='Describes the table; rendered as a <caption> for accessibility.')
    columns = blocks.ListBlock(TableColumnBlock(), default=[], label='Columns')
    rows = blocks.ListBlock(TableRowBlock(), default=[], label='Rows')
    data_source = blocks.StreamBlock([
        ('books', BooksSourceBlock()),
        ('news', NewsSourceBlock()),
        ('book_resources', BookResourcesSourceBlock()),
        ('subjects', SubjectsSourceBlock()),
        ('endpoint', EndpointSourceBlock()),
    ], max_num=1, required=False, label='Data source',
        help_text='Fill the table from CMS content instead of manual rows. '
                  'When set, manual Columns and Rows are ignored.')
    config = blocks.StreamBlock([
        ('striped', blocks.ChoiceBlock(choices=[('off', 'Off'), ('on', 'On')],
            help_text='Shade alternating rows. Default shade unless Row Colors is set.')),
        ('row_colors', blocks.RegexBlock(
            regex=r'^#[0-9a-fA-F]{6}(\s*,\s*#[0-9a-fA-F]{6})*$', required=False,
            label='Row Colors',
            help_text='Comma-separated hex colors cycled across body rows, e.g. #ffffff,#f2f2f2. Overrides the default zebra shade.',
            error_messages={'invalid': 'Must be comma-separated hex colors. eg: #ffffff,#f2f2f2.'})),
        ('condensed', blocks.ChoiceBlock(choices=[('off', 'Off'), ('on', 'On')],
            help_text='Tighter cell padding.')),
        ('sortable', blocks.ChoiceBlock(choices=[('off', 'Off'), ('on', 'On')],
            help_text='Let readers sort by clicking column headers.')),
        ('filterable', blocks.ChoiceBlock(choices=[('off', 'Off'), ('on', 'On')],
            help_text='Show a text box that filters rows by their content.')),
        ('default_sort_column', blocks.IntegerBlock(min_value=1,
            help_text='1-based column number the table is sorted by on load.')),
        ('default_sort_direction', blocks.ChoiceBlock(choices=[
            ('asc', 'Ascending'), ('desc', 'Descending')],
            help_text='Direction for the default sort. Default ascending.')),
        ('row_limit', blocks.IntegerBlock(min_value=1,
            help_text='Show at most this many rows, with a "Show more" control for the rest.')),
        ('empty_message', blocks.CharBlock(required=False,
            help_text='Shown when the table has no rows (e.g. a dynamic source returns nothing).')),
        ('id', id_config_block()),
    ], block_counts={
        'striped': {'max_num': 1},
        'row_colors': {'max_num': 1},
        'condensed': {'max_num': 1},
        'sortable': {'max_num': 1},
        'filterable': {'max_num': 1},
        'default_sort_column': {'max_num': 1},
        'default_sort_direction': {'max_num': 1},
        'row_limit': {'max_num': 1},
        'empty_message': {'max_num': 1},
        'id': {'max_num': 1},
    }, required=False, collapsed=True)

    class Meta:
        label = 'Table'
        icon = 'table'
        collapsed = True

    def get_api_representation(self, value, context=None):
        from pages import table_sources

        rep = super().get_api_representation(value, context)
        rep.pop('data_source', None)
        stream = value.get('data_source')
        if not stream:
            return rep

        child = stream[0]
        # Snapshot key: hash of the stored (JSON-safe) source spec, so the
        # last good result survives a source outage at serialize time.
        # Best-effort: the default cache here is per-process LocMem, so the
        # snapshot does not survive restarts and is not shared across
        # workers — a shared backend (e.g. Redis) would upgrade this.
        cache_key = None
        try:
            spec = child.block.get_prep_value(child.value)
            cache_key = 'table_block_snapshot:' + hashlib.sha256(
                json.dumps({'type': child.block_type, 'value': spec},
                           sort_keys=True, default=str).encode()).hexdigest()
            data = table_sources.resolve_data_source(child.block_type, child.value)
            # 30-day TTL: bounds key accumulation on shared backends while
            # keeping the fallback useful; older snapshots are stale anyway.
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
        except Exception as e:
            capture_exception(e)
            data = (cache.get(cache_key) if cache_key else None) or {'columns': [], 'rows': []}
        rep['columns'] = data['columns']
        rep['rows'] = data['rows']
        return rep
