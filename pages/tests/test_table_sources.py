import datetime

from django.test import TestCase

from pages.table_sources import build_cell, build_table, field_choices


class BuildCellTests(TestCase):
    def test_text_cell_escapes_html(self):
        cell = build_cell('<script>x</script>', 'text')
        self.assertEqual(cell['cta'], [])
        self.assertNotIn('<script>', cell['content'])
        self.assertIn('&lt;script&gt;', cell['content'])

    def test_empty_value_yields_empty_cell(self):
        self.assertEqual(build_cell(None, 'text'), {'content': '', 'cta': []})
        self.assertEqual(build_cell('', 'text'), {'content': '', 'cta': []})

    def test_date_cell_formats_mm_dd_yyyy(self):
        cell = build_cell(datetime.date(2018, 3, 28), 'date')
        self.assertEqual(cell['content'], '03/28/2018')

    def test_number_cell_stringifies(self):
        self.assertEqual(build_cell(42, 'number')['content'], '42')

    def test_link_cell_builds_cta_shape(self):
        cell = build_cell({'text': 'Biology 2e', 'url': '/details/books/biology-2e'}, 'link')
        self.assertEqual(cell['content'], '')
        cta = cell['cta'][0]
        self.assertEqual(cta['text'], 'Biology 2e')
        self.assertEqual(cta['target'], {'value': '/details/books/biology-2e', 'type': 'internal'})
        self.assertEqual(cta['aria_label'], '')
        self.assertEqual(cta['config'], [])

    def test_link_cell_absolute_url_is_external(self):
        cell = build_cell({'text': 'Read', 'url': 'https://example.com/x'}, 'link')
        self.assertEqual(cell['cta'][0]['target']['type'], 'external')

    def test_link_cell_without_url_falls_back_to_text(self):
        cell = build_cell({'text': 'No link', 'url': ''}, 'link')
        self.assertEqual(cell['cta'], [])
        self.assertEqual(cell['content'], 'No link')

    def test_image_cell_renders_img_tag(self):
        cell = build_cell({'url': 'https://assets.openstax.org/x.png', 'alt': 'Cover'}, 'image')
        self.assertIn('<img', cell['content'])
        self.assertIn('src="https://assets.openstax.org/x.png"', cell['content'])
        self.assertIn('alt="Cover"', cell['content'])

    def test_html_cell_passes_through(self):
        cell = build_cell('<p>rich</p>', 'html')
        self.assertEqual(cell['content'], '<p>rich</p>')

    def test_link_cell_mailto_and_protocol_relative_are_external(self):
        for url in ['mailto:info@openstax.org', 'tel:+17133486000', '//cdn.example.com/x']:
            cell = build_cell({'text': 'Contact', 'url': url}, 'link')
            self.assertEqual(cell['cta'][0]['target']['type'], 'external', url)

    def test_date_cell_non_date_fallback_is_escaped(self):
        cell = build_cell('<b>not a date</b>', 'date')
        self.assertNotIn('<b>', cell['content'])
        self.assertIn('&lt;b&gt;', cell['content'])


class BuildTableTests(TestCase):
    REGISTRY = {
        'name': ('Name', lambda item: item['name'], 'text'),
        'when': ('Date', lambda item: item['when'], 'date'),
        'boom': ('Boom', lambda item: 1 / 0, 'text'),
    }

    def test_builds_columns_and_rows_from_registry(self):
        result = build_table(
            [{'field': 'name', 'header': '', 'type': ''},
             {'field': 'when', 'header': 'Published', 'type': ''}],
            self.REGISTRY,
            [{'name': 'Biology 2e', 'when': datetime.date(2018, 3, 28)}],
        )
        self.assertEqual(result['columns'], [
            {'header': 'Name', 'type': 'text'},
            {'header': 'Published', 'type': 'date'},
        ])
        cells = result['rows'][0]['cells']
        self.assertEqual(cells[0]['content'], 'Biology 2e')
        self.assertEqual(cells[1]['content'], '03/28/2018')

    def test_explicit_type_overrides_registry_default(self):
        result = build_table(
            [{'field': 'when', 'header': '', 'type': 'text'}],
            self.REGISTRY,
            [{'when': datetime.date(2018, 3, 28)}],
        )
        self.assertEqual(result['columns'][0]['type'], 'text')

    def test_failing_getter_yields_empty_cell_not_error(self):
        result = build_table(
            [{'field': 'boom', 'header': '', 'type': ''}],
            self.REGISTRY,
            [{'name': 'x'}],
        )
        self.assertEqual(result['rows'][0]['cells'][0], {'content': '', 'cta': []})

    def test_field_choices_from_registry(self):
        self.assertIn(('name', 'Name'), field_choices(self.REGISTRY))

    def test_unknown_field_is_skipped_without_error(self):
        result = build_table(
            [{'field': 'gone', 'header': '', 'type': ''},
             {'field': 'name', 'header': '', 'type': ''}],
            self.REGISTRY,
            [{'name': 'x'}],
        )
        self.assertEqual(len(result['columns']), 1)
        self.assertEqual(len(result['rows'][0]['cells']), 1)
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'x')

    def test_link_column_collapses_to_text_column_type(self):
        registry = {'link': ('Link', lambda item: {'text': 't', 'url': '/x'}, 'link')}
        result = build_table(
            [{'field': 'link', 'header': '', 'type': ''}],
            registry,
            [{}],
        )
        self.assertEqual(result['columns'][0]['type'], 'text')
