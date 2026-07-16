import hashlib
import json

from django.core.cache import cache
from sentry_sdk import capture_exception
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock

from openstax.api_fields import APIRichTextBlock
from pages.shared_blocks import CTALinkBlock, id_config_block
from pages.table_sources import (
    SOURCE_CELL_TYPE_CHOICES, field_choices,
    BOOK_FIELDS, NEWS_FIELDS, RESOURCE_FIELDS, SUBJECT_FIELDS,
)


def _manual_cell_from_api_value(cell_type, api_value):
    if cell_type == 'cta':
        return {'content': '', 'cta': api_value or []}
    if cell_type == 'date':
        return {'content': api_value.strftime('%m/%d/%Y') if api_value else '', 'cta': []}
    return {'content': api_value or '', 'cta': []}


def _manual_table_representation(manual_rep, renderer_column_types):
    """manual_rep is TypedTableBlock's own get_api_representation() output:
    {'columns': [{'type': block_name, 'heading': str}], 'rows': [{'values': [...]}], 'caption': str}.
    Reshapes it into the renderer's {'columns': [{'header', 'type'}], 'rows': [{'cells': [{'content','cta'}]}]}."""
    columns = manual_rep['columns']
    out_columns = [
        {'header': col['heading'],
         'type': col['type'] if col['type'] in renderer_column_types else 'text'}
        for col in columns
    ]
    out_rows = []
    for row in manual_rep['rows']:
        cells = [
            _manual_cell_from_api_value(col['type'], value)
            for col, value in zip(columns, row['values'])
        ]
        out_rows.append({'cells': cells})
    return {'columns': out_columns, 'rows': out_rows}


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


class TableBlock(blocks.StructBlock):
    caption = blocks.CharBlock(required=False,
        help_text='Describes the table; rendered as a <caption> for accessibility.')
    manual = TypedTableBlock([
        ('text', blocks.CharBlock(required=False)),
        ('number', blocks.CharBlock(required=False)),
        ('date', blocks.DateBlock(required=False)),
        ('rich_text', APIRichTextBlock(required=False)),
        ('cta', blocks.ListBlock(CTALinkBlock(required=False), default=[], max_num=1, label='CTA')),
    ], required=False, label='Manual table',
        help_text='Authored columns and rows. Ignored when a Data source is set below.')
    data_source = blocks.StreamBlock([
        ('books', BooksSourceBlock()),
        ('news', NewsSourceBlock()),
        ('book_resources', BookResourcesSourceBlock()),
        ('subjects', SubjectsSourceBlock()),
        ('endpoint', EndpointSourceBlock()),
    ], max_num=1, required=False, label='Data source',
        help_text='Fill the table from CMS content instead of manual rows. '
                  'When set, the manual table is ignored.')
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
        manual_rep = rep.pop('manual')
        rep.pop('data_source', None)
        stream = value.get('data_source')
        if not stream:
            rep.update(_manual_table_representation(manual_rep, table_sources.RENDERER_COLUMN_TYPES))
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
