from unittest import mock

from django.core.cache import cache
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


class DynamicTableBlockTests(TestCase):
    def setUp(self):
        cache.clear()

    def _dynamic_value(self):
        block = TableBlock()
        return block, block.to_python({
            'caption': 'Live books',
            'columns': [], 'rows': [],
            'data_source': [{'type': 'subjects', 'value': {
                'variant': 'he', 'k12_category': '',
                'columns': [{'field': 'name', 'header': '', 'type': ''}],
            }}],
            'config': [],
        })

    def test_data_source_never_appears_in_api_output(self):
        block, value = self._dynamic_value()
        rep = block.get_api_representation(value)
        self.assertNotIn('data_source', rep)

    def test_hydrates_columns_and_rows_from_resolver(self):
        from wagtail.models import Locale
        from snippets.models import Subject
        Subject.objects.create(name='Math', locale=Locale.get_default())
        block, value = self._dynamic_value()
        rep = block.get_api_representation(value)
        self.assertEqual(rep['columns'], [{'header': 'Subject', 'type': 'text'}])
        self.assertEqual(rep['rows'][0]['cells'][0]['content'], 'Math')

    def test_resolver_failure_falls_back_to_snapshot(self):
        from wagtail.models import Locale
        from snippets.models import Subject
        Subject.objects.create(name='Math', locale=Locale.get_default())
        block, value = self._dynamic_value()
        block.get_api_representation(value)  # primes the snapshot cache
        with mock.patch('pages.table_sources.resolve_subjects',
                        side_effect=RuntimeError('source down')):
            rep = block.get_api_representation(value)
        self.assertEqual(rep['rows'][0]['cells'][0]['content'], 'Math')

    def test_key_computation_failure_yields_empty_table_not_error(self):
        block, value = self._dynamic_value()
        with mock.patch('pages.table_block.json.dumps',
                        side_effect=RuntimeError('unhashable spec')):
            rep = block.get_api_representation(value)
        self.assertEqual(rep['columns'], [])
        self.assertEqual(rep['rows'], [])

    def test_resolver_failure_without_snapshot_yields_empty_table(self):
        block, value = self._dynamic_value()
        with mock.patch('pages.table_sources.resolve_subjects',
                        side_effect=RuntimeError('source down')):
            rep = block.get_api_representation(value)
        self.assertEqual(rep['columns'], [])
        self.assertEqual(rep['rows'], [])

    def test_resolver_failure_reports_to_sentry(self):
        block, value = self._dynamic_value()
        with mock.patch('pages.table_sources.resolve_subjects',
                        side_effect=RuntimeError('source down')), \
             mock.patch('pages.table_block.capture_exception') as capture:
            block.get_api_representation(value)
        capture.assert_called_once()

    def test_manual_table_without_source_is_unchanged(self):
        block = TableBlock()
        value = block.to_python({
            'caption': '', 'data_source': [], 'config': [],
            'columns': [{'header': 'A', 'type': ''}],
            'rows': [{'cells': [{'content': '<p>x</p>', 'cta': []}]}],
        })
        rep = block.get_api_representation(value)
        self.assertEqual(rep['columns'][0]['header'], 'A')
        self.assertIn('x', rep['rows'][0]['cells'][0]['content'])


class ManualFieldDefinitionTests(TestCase):
    def test_manual_field_is_typed_table_block_with_expected_cell_types(self):
        from wagtail.contrib.typed_table_block.blocks import TypedTableBlock

        block = TableBlock()
        manual_block = block.child_blocks['manual']
        self.assertIsInstance(manual_block, TypedTableBlock)
        self.assertEqual(
            set(manual_block.child_blocks.keys()),
            {'text', 'number', 'date', 'rich_text', 'cta'},
        )
