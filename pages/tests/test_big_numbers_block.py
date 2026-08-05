from django.test import TestCase

from pages.custom_blocks import BigNumberBlock, BigNumbersBlock


class BigNumbersBlockContentTests(TestCase):
    def test_content_field_only_allows_big_number(self):
        content_block = BigNumbersBlock().child_blocks['content']
        self.assertEqual(list(content_block.child_blocks.keys()), ['big_number'])

    def test_big_number_block_has_expected_fields(self):
        big_number_block = BigNumbersBlock().child_blocks['content'].child_blocks['big_number']
        self.assertIn('number', big_number_block.child_blocks)
        self.assertIn('caption', big_number_block.child_blocks)
        self.assertIn('color', big_number_block.child_blocks)

    def test_content_accepts_big_numbers(self):
        block = BigNumbersBlock()
        value = block.to_python({
            'content': [
                {'type': 'big_number', 'value': {
                    'number': '8M+',
                    'caption': 'Students reached',
                    'color': 'blue',
                }},
                {'type': 'big_number', 'value': {
                    'number': '40+',
                    'caption': 'Titles published',
                    'color': '',
                }},
            ],
        })
        rep = block.get_api_representation(value)
        content = rep['content']
        self.assertEqual(content[0]['type'], 'big_number')
        self.assertEqual(content[0]['value']['number'], '8M+')
        self.assertEqual(content[0]['value']['caption'], 'Students reached')
        self.assertEqual(content[0]['value']['color'], 'blue')
        self.assertEqual(content[1]['type'], 'big_number')
        self.assertEqual(content[1]['value']['number'], '40+')

    def test_content_defaults_to_empty_and_is_not_required(self):
        block = BigNumbersBlock()
        value = block.to_python({})
        rep = block.get_api_representation(value)
        self.assertEqual(rep['content'], [])

    def test_number_is_required_caption_and_color_are_not(self):
        big_number_block = BigNumberBlock()
        self.assertTrue(big_number_block.child_blocks['number'].required)
        self.assertFalse(big_number_block.child_blocks['caption'].required)
        self.assertFalse(big_number_block.child_blocks['color'].required)
