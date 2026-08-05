from django.test import TestCase

from pages.custom_blocks import FAQBlock
from pages.table_block import TableBlock


class FAQBlockContentTests(TestCase):
    def test_content_field_accepts_table_and_text(self):
        block = FAQBlock()
        value = block.to_python({
            'question': '<p>What formats are available?</p>',
            'slug': 'formats',
            'answer': '<p>See the table below.</p>',
            'document': None,
            'content': [
                {'type': 'table', 'value': {
                    'caption': 'Formats',
                    'columns': [{'header': 'Format', 'type': ''}],
                    'rows': [{'cells': [{'content': '<p>PDF</p>', 'cta': []}]}],
                }},
                {'type': 'text', 'value': '<p>Extra note.</p>'},
            ],
        })
        rep = block.get_api_representation(value)
        content = rep['content']
        self.assertEqual(content[0]['type'], 'table')
        self.assertEqual(content[0]['value']['columns'][0]['header'], 'Format')
        self.assertEqual(content[1]['type'], 'text')
        self.assertIn('Extra note', content[1]['value'])

    def test_content_field_has_image_option_with_alt_text(self):
        content_block = FAQBlock().child_blocks['content']
        image_option = content_block.child_blocks['image']
        self.assertIn('alt_text', image_option.child_blocks)
        self.assertIn('image', image_option.child_blocks)

    def test_content_defaults_to_empty_and_is_not_required(self):
        block = FAQBlock()
        value = block.to_python({
            'question': '<p>Q</p>', 'slug': 'q', 'answer': '<p>A</p>', 'document': None,
        })
        rep = block.get_api_representation(value)
        self.assertEqual(rep['content'], [])

    def test_table_block_collapsed_by_default(self):
        self.assertTrue(TableBlock().meta.collapsed)
