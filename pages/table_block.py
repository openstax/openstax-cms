from wagtail import blocks

from openstax.api_fields import APIRichTextBlock
from pages.custom_blocks import CTALinkBlock, id_config_block


# User-facing column sort types (renderer uses these to pick a comparator).
COLUMN_TYPE_CHOICES = [
    ('text', 'Text'),
    ('number', 'Number'),
    ('date', 'Date'),
]


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
    }, required=False)

    class Meta:
        label = 'Table'
        icon = 'table'
