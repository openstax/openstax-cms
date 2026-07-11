from django.test import TestCase

from pages.custom_blocks import CTAButtonBarBlock, DividerBlock, LinksGroupBlock, PersonBlock, QuoteBlock
from pages.models.constants import BASE_CONTENT_BLOCKS, BODY_BLOCKS, SECTION_CONTENT_BLOCKS
from pages.models.core import RootPage
from pages.shared_blocks import CTALinkBlock
from pages.table_block import TableBlock


class ConfigStreamsCollapsedTests(TestCase):
    def test_named_block_configs_collapsed(self):
        for block_class in (
            CTALinkBlock, LinksGroupBlock, CTAButtonBarBlock,
            QuoteBlock, DividerBlock, PersonBlock, TableBlock,
        ):
            with self.subTest(block=block_class.__name__):
                self.assertTrue(block_class().child_blocks['config'].meta.collapsed)

    def test_content_block_configs_collapsed(self):
        cards_block = dict(BASE_CONTENT_BLOCKS)['cards_block']
        self.assertTrue(cards_block.child_blocks['config'].meta.collapsed)

    def test_well_config_collapsed(self):
        well = dict(SECTION_CONTENT_BLOCKS)['well']
        self.assertTrue(well.child_blocks['config'].meta.collapsed)

    def test_hero_and_section_and_columns_configs_collapsed(self):
        body_blocks = dict(BODY_BLOCKS)
        for name in ('hero', 'section', 'columns'):
            with self.subTest(block=name):
                self.assertTrue(body_blocks[name].child_blocks['config'].meta.collapsed)

    def test_tabbed_content_config_collapsed(self):
        body_stream_block = RootPage._meta.get_field('body').stream_block
        tabbed_content = body_stream_block.child_blocks['tabbed_content']
        self.assertTrue(tabbed_content.child_blocks['config'].meta.collapsed)
