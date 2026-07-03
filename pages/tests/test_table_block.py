from django.test import TestCase

from pages.models.constants import BASE_CONTENT_BLOCKS
from pages.table_block import TableBlock


class TableBlockRegistrationTests(TestCase):
    def test_table_registered_in_base_content_blocks(self):
        names = [name for name, _ in BASE_CONTENT_BLOCKS]
        self.assertIn('table', names)


class ManualTableBlockTests(TestCase):
    def _value(self, **overrides):
        data = {
            'caption': 'OpenStax books',
            'columns': [
                {'header': 'Title', 'type': ''},
                {'header': 'Published', 'type': 'date'},
            ],
            'rows': [
                {'cells': [
                    {'content': '<p>Biology 2e</p>', 'cta': []},
                    {'content': '<p>2018</p>', 'cta': []},
                ]},
            ],
            'config': [],
        }
        data.update(overrides)
        return data

    def test_manual_serialization_matches_renderer_contract(self):
        block = TableBlock()
        value = block.to_python(self._value())
        rep = block.get_api_representation(value)
        self.assertEqual(rep['caption'], 'OpenStax books')
        self.assertEqual(rep['columns'][0]['header'], 'Title')
        self.assertEqual(rep['columns'][1]['type'], 'date')
        cell = rep['rows'][0]['cells'][0]
        self.assertIn('Biology 2e', cell['content'])
        self.assertEqual(cell['cta'], [])

    def test_cta_cell_serializes_ctalink_shape(self):
        block = TableBlock()
        value = block.to_python(self._value(rows=[
            {'cells': [{'content': '', 'cta': [{
                'text': 'View book',
                'aria_label': '',
                'target': [{'type': 'external', 'value': 'https://openstax.org/details/books/biology-2e'}],
                'config': [],
            }]}]},
        ]))
        rep = block.get_api_representation(value)
        cta = rep['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['text'], 'View book')
        self.assertEqual(cta['target'], {
            'value': 'https://openstax.org/details/books/biology-2e',
            'type': 'external',
        })

    def test_config_options_serialize_as_type_value_pairs(self):
        block = TableBlock()
        value = block.to_python(self._value(config=[
            {'type': 'striped', 'value': 'on'},
            {'type': 'row_limit', 'value': 10},
            {'type': 'empty_message', 'value': 'No books match.'},
            {'type': 'default_sort_column', 'value': 1},
            {'type': 'default_sort_direction', 'value': 'desc'},
        ]))
        rep = block.get_api_representation(value)
        entries = {e['type']: e['value'] for e in rep['config']}
        self.assertEqual(entries['striped'], 'on')
        self.assertEqual(entries['row_limit'], 10)
        self.assertEqual(entries['empty_message'], 'No books match.')
        self.assertEqual(entries['default_sort_column'], 1)
        self.assertEqual(entries['default_sort_direction'], 'desc')
