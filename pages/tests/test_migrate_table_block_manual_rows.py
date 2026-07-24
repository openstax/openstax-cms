import importlib

from django.test import SimpleTestCase, TestCase
from wagtail.models import Page

from news.models import PressIndex
from pages.models import RootPage

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


def _old_shape_faq(faq_id='faq-1', table_id='table-1'):
    """An old-shape 'faq' StreamField block whose nested FAQBlock.content
    carries a 'table' block still in the pre-migration columns/rows shape,
    matching what real pre-existing PressIndex.faqs data looks like."""
    return {
        'type': 'faq', 'id': faq_id,
        'value': {
            'question': 'Why?',
            'slug': 'why',
            'answer': 'Because.',
            'document': None,
            'content': [{
                'type': 'table', 'id': table_id,
                'value': {
                    'caption': '', 'data_source': [], 'config': [],
                    'columns': [{'header': 'Title', 'type': ''}],
                    'rows': [{'cells': [{'content': 'x', 'cta': []}]}],
                },
            }],
        },
    }


class MigrateStreamFieldPressIndexTests(TestCase):
    """Covers the model-dispatch wiring: migrate_table_manual_rows (via
    _migrate_stream_field) must also walk news.PressIndex.faqs, not just
    pages.RootPage.body — the pure transform functions (_migrate_table_value,
    _fix_stream) are already covered above regardless of which model calls
    them."""

    def setUp(self):
        root_page = Page.objects.get(title='Root')
        homepage = RootPage(title='Hello World', slug='hello-world-press')
        root_page.add_child(instance=homepage)

        self.press_index = PressIndex(
            title='Press Index',
            slug='press-migrate-test',
            press_inquiry_phone='111-111-1111',
            press_inquiry_email='press@example.com',
            experts_heading='experts heading',
            experts_blurb='experts blurb',
            faqs=[_old_shape_faq()],
        )
        homepage.add_child(instance=self.press_index)

    def test_migrate_stream_field_converts_old_shape_table_in_press_index_faqs(self):
        page = PressIndex.objects.get(id=self.press_index.id)
        raw_before = list(page.faqs.raw_data)
        table_value_before = raw_before[0]['value']['content'][0]['value']
        self.assertIn('columns', table_value_before)
        self.assertIn('rows', table_value_before)

        migration._migrate_stream_field(PressIndex.objects.filter(id=page.id), 'faqs')

        page.refresh_from_db()
        raw_after = list(page.faqs.raw_data)
        table_value_after = raw_after[0]['value']['content'][0]['value']
        self.assertNotIn('columns', table_value_after)
        self.assertNotIn('rows', table_value_after)
        self.assertEqual(table_value_after['manual']['columns'], [{'type': 'text', 'heading': 'Title'}])
        self.assertEqual(table_value_after['manual']['rows'][0]['values'][0], 'x')

    def test_migrate_table_manual_rows_dispatches_to_press_index_faqs(self):
        # Stand in for the migration framework's historical `apps.get_model`
        # with the real current model classes — _fix_stream/_migrate_table_value
        # are pure functions over raw JSON, so this exercises the real
        # dispatch (which model/field pairs get walked) without needing a
        # full MigrationExecutor run.
        fake_apps = _FakeApps({
            ('pages', 'RootPage'): RootPage,
            ('news', 'PressIndex'): PressIndex,
        })

        migration.migrate_table_manual_rows(fake_apps, schema_editor=None)

        page = PressIndex.objects.get(id=self.press_index.id)
        raw_after = list(page.faqs.raw_data)
        table_value_after = raw_after[0]['value']['content'][0]['value']
        self.assertNotIn('columns', table_value_after)
        self.assertNotIn('rows', table_value_after)
        self.assertEqual(table_value_after['manual']['rows'][0]['values'][0], 'x')


class _FakeApps:
    """Minimal stand-in for the migration framework's historical `apps`,
    resolving get_model() to real current model classes."""

    def __init__(self, models):
        self._models = models

    def get_model(self, app_label, model_name):
        return self._models[(app_label, model_name)]
