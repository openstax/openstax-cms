import io

from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page

from pages.models import RootPage


def _table_block(columns, rows, id='table-1'):
    return {
        'type': 'table', 'id': id,
        'value': {
            'caption': '', 'data_source': [], 'config': [],
            'manual': {'columns': columns, 'rows': rows, 'caption': ''},
        },
    }


def _section_wrapping(table_block, id='section-1'):
    # `table` is only a valid child of a container block's `content`
    # StreamBlock (e.g. `section`) — it is NOT a top-level RootPage.body
    # block. StreamBlock.to_python() silently drops any raw block whose
    # `type` isn't in that StreamBlock's own child_blocks (see
    # wagtail/blocks/stream_block.py), so a table placed directly at the
    # top level of `body` disappears with no error. Real content mirrors
    # this: every table in the audited k12-subjects-staxify page is nested
    # inside a section/hero/tabbed_content, never at the body's top level.
    return {
        'type': 'section', 'id': id,
        'value': {'content': [table_block], 'config': []},
    }


class FindResourceTablesTests(TestCase):
    def setUp(self):
        self.root = Page.objects.get(title='Root')

    def _create_page(self, slug, body):
        page = RootPage(title=slug, slug=slug, body=body)
        self.root.add_child(instance=page)
        # publish the page so it appears in live() queryset
        revision = page.save_revision()
        revision.publish()
        # Reload from database to ensure latest data
        return RootPage.objects.get(id=page.id)

    def test_flags_table_matching_book_resources_shape(self):
        page = self._create_page('resources-dupe', [_section_wrapping(_table_block(
            columns=[
                {'type': 'text', 'heading': 'Resource'},
                {'type': 'text', 'heading': 'Book(s)'},
                {'type': 'cta', 'heading': 'Access'},
            ],
            rows=[{'values': ['Guide', 'Prealgebra 2e', []]}],
        ))])
        out = io.StringIO()
        call_command('find_resource_tables', stdout=out)
        output = out.getvalue()
        self.assertIn(str(page.id), output)
        self.assertIn('Book(s)', output)

    def test_does_not_flag_table_without_cta_column(self):
        self._create_page('plain-table', [_section_wrapping(_table_block(
            columns=[
                {'type': 'text', 'heading': 'Book(s)'},
                {'type': 'text', 'heading': 'Notes'},
            ],
            rows=[{'values': ['Prealgebra 2e', 'note']}],
        ))])
        out = io.StringIO()
        call_command('find_resource_tables', stdout=out)
        self.assertIn('No candidate tables found.', out.getvalue())

    def test_does_not_flag_table_with_data_source(self):
        page = self._create_page('dynamic-table', [_section_wrapping({
            'type': 'table', 'id': 'x',
            'value': {
                'caption': '', 'config': [],
                'manual': {'columns': [], 'rows': [], 'caption': ''},
                'data_source': [{'type': 'book_resources', 'value': {}}],
            },
        })])
        out = io.StringIO()
        call_command('find_resource_tables', stdout=out)
        self.assertNotIn(str(page.id), out.getvalue())
