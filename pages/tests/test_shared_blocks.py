from django.core.exceptions import ValidationError
from django.test import TestCase

from pages.shared_blocks import (
    CTALinkBlock, LinkInfoBlock, OpenStaxColorBlock, gradient_block_counts,
    gradient_config_options, hex_color_block, id_config_block,
)


class SharedBlocksImportTests(TestCase):
    def test_hex_color_block_returns_openstax_color_block(self):
        block = hex_color_block('Pick a color.')
        self.assertIsInstance(block, OpenStaxColorBlock)
        self.assertEqual(block.field.help_text, 'Pick a color.')

    def test_id_config_block_rejects_invalid_id(self):
        block = id_config_block()
        with self.assertRaises(ValidationError):
            block.clean('not a valid id!')

    def test_gradient_config_options_and_counts_match(self):
        names = [name for name, _ in gradient_config_options()]
        self.assertEqual(set(names), set(gradient_block_counts().keys()))

    def test_cta_link_block_serializes_via_link_info_block(self):
        self.assertTrue(issubclass(CTALinkBlock, LinkInfoBlock))
        block = CTALinkBlock()
        value = block.to_python({
            'text': 'View book',
            'aria_label': '',
            'target': [{'type': 'external', 'value': 'https://openstax.org'}],
            'config': [],
        })
        rep = block.get_api_representation(value)
        self.assertEqual(rep['text'], 'View book')
        self.assertEqual(rep['target'], {'value': 'https://openstax.org', 'type': 'external'})
