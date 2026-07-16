import importlib

from django.test import SimpleTestCase

migration = importlib.import_module('pages.migrations.0200_migrate_table_block_manual_rows')


class MigrateTableValueTests(SimpleTestCase):
    def test_book_resources_shaped_table_classifies_correctly(self):
        # NOTE: 'target' below is the CTALinkBlock's raw STORED shape — a
        # StreamField list [{'type', 'value', 'id'}] — not the flattened
        # {'value', 'type'} dict LinkBlock.get_api_representation produces
        # for API output (pages/shared_blocks.py:169). Migrations manipulate
        # raw stored JSON end-to-end, so both input and output here use the
        # storage shape; there is no flattening step at any point.
        value = {
            'caption': '',
            'columns': [
                {'header': 'Resource', 'type': ''},
                {'header': 'Description', 'type': ''},
                {'header': 'Book(s)', 'type': ''},
                {'header': 'Access', 'type': ''},
            ],
            'rows': [
                {'cells': [
                    {'content': 'Instructor Getting Started Guide', 'cta': []},
                    {'content': '<p>Download our helpful guide.</p>', 'cta': []},
                    {'content': 'Prealgebra 2e', 'cta': []},
                    {'content': '', 'cta': [{
                        'text': 'Download', 'aria_label': '',
                        'target': [{'type': 'external', 'value': 'https://assets.openstax.org/guide.pdf', 'id': 'x1'}],
                        'config': [],
                    }]},
                ]},
            ],
            'data_source': [],
            'config': [],
        }
        changed = migration._migrate_table_value(value)
        self.assertTrue(changed)
        self.assertNotIn('columns', value)
        self.assertNotIn('rows', value)
        self.assertEqual(value['manual']['columns'], [
            {'type': 'text', 'heading': 'Resource'},
            {'type': 'rich_text', 'heading': 'Description'},
            {'type': 'text', 'heading': 'Book(s)'},
            {'type': 'cta', 'heading': 'Access'},
        ])
        self.assertEqual(value['manual']['rows'][0]['values'][0], 'Instructor Getting Started Guide')
        self.assertEqual(value['manual']['rows'][0]['values'][1], '<p>Download our helpful guide.</p>')
        self.assertEqual(value['manual']['rows'][0]['values'][3][0]['text'], 'Download')
        self.assertEqual(
            value['manual']['rows'][0]['values'][3][0]['target'],
            [{'type': 'external', 'value': 'https://assets.openstax.org/guide.pdf', 'id': 'x1'}],
        )

    def test_dynamic_table_with_data_source_is_left_untouched(self):
        value = {
            'caption': '', 'columns': [], 'rows': [],
            'data_source': [{'type': 'books', 'value': {'columns': []}}],
            'config': [],
        }
        changed = migration._migrate_table_value(value)
        self.assertFalse(changed)
        self.assertIn('columns', value)
        self.assertIn('rows', value)

    def test_empty_manual_table_still_migrates_to_empty_manual_field(self):
        value = {'caption': '', 'columns': [], 'rows': [], 'data_source': [], 'config': []}
        changed = migration._migrate_table_value(value)
        self.assertTrue(changed)
        self.assertEqual(value['manual']['columns'], [])
        self.assertEqual(value['manual']['rows'], [])

    def test_fix_stream_finds_table_nested_inside_section_and_tabbed_content(self):
        raw = [{
            'type': 'section', 'id': 'a',
            'value': {'content': [{
                'type': 'tabbed_content', 'id': 'b',
                'value': {'content': [{
                    'type': 'table', 'id': 'c',
                    'value': {
                        'caption': '', 'data_source': [], 'config': [],
                        'columns': [{'header': 'Title', 'type': ''}],
                        'rows': [{'cells': [{'content': 'x', 'cta': []}]}],
                    },
                }]},
            }]},
        }]
        changed = migration._fix_stream(raw)
        self.assertTrue(changed)
        table_value = raw[0]['value']['content'][0]['value']['content'][0]['value']
        self.assertEqual(table_value['manual']['rows'][0]['values'][0], 'x')
