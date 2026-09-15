import re

from django.core.exceptions import ValidationError
from django.test import TestCase

from pages.custom_blocks import CTAButtonBarBlock
from pages.models.constants import BODY_BLOCKS
from pages.shared_blocks import (
    AUDIENCE_CONDITION_CHOICES, CollapsedHTMLBlock, CTALinkBlock, LinkInfoBlock, OpenStaxColorBlock,
    RenderingConditionBlock, gradient_block_counts, gradient_config_options, hex_color_block,
    id_config_block, rendering_condition_block,
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


class RenderingConditionBlockTests(TestCase):
    def test_accepts_multiple_selections(self):
        block = rendering_condition_block()
        value = block.to_python(['role:student', 'role:instructor'])
        self.assertEqual(value, ['role:student', 'role:instructor'])

    def test_choice_values_match_the_agreed_vocabulary(self):
        values = [value for value, _label in AUDIENCE_CONDITION_CHOICES]
        self.assertEqual(values, [
            'role:anonymous', 'role:student', 'role:instructor', 'role:admin',
            'status:verified', 'status:pending', 'school:assignable', 'adopter:yes',
        ])

    def test_get_api_representation_joins_several_values(self):
        block = rendering_condition_block()
        rep = block.get_api_representation(['role:student', 'role:instructor'])
        self.assertEqual(rep, 'role:student,role:instructor')

    def test_get_api_representation_single_value_has_no_comma(self):
        block = rendering_condition_block()
        rep = block.get_api_representation(['role:student'])
        self.assertEqual(rep, 'role:student')
        self.assertNotIn(',', rep)

    def test_get_api_representation_empty_or_none_is_blank_string(self):
        block = rendering_condition_block()
        self.assertEqual(block.get_api_representation([]), '')
        self.assertEqual(block.get_api_representation(None), '')

    def test_tolerates_a_legacy_comma_joined_string_value(self):
        # A page revision saved back when this field was a free-text CharBlock
        # could hold a bare string rather than a list; to_python must not error.
        block = rendering_condition_block()
        value = block.to_python('role:student,role:instructor')
        self.assertEqual(value, ['role:student', 'role:instructor'])

    def test_tolerates_a_legacy_single_string_value_with_no_comma(self):
        block = rendering_condition_block()
        value = block.to_python('role:student')
        self.assertEqual(value, ['role:student'])

    def test_rendering_condition_present_in_cta_button_bar_config(self):
        config = CTAButtonBarBlock().child_blocks['config']
        self.assertIsInstance(config.child_blocks['rendering_condition'], RenderingConditionBlock)
        self.assertEqual(config.meta.block_counts['rendering_condition'], {'max_num': 1})

    def test_rendering_condition_present_in_hero_and_section_config(self):
        body_blocks = dict(BODY_BLOCKS)
        for name in ('hero', 'section'):
            with self.subTest(block=name):
                config = body_blocks[name].child_blocks['config']
                self.assertIsInstance(config.child_blocks['rendering_condition'], RenderingConditionBlock)
                self.assertEqual(config.meta.block_counts['rendering_condition'], {'max_num': 1})

    def test_serializes_through_the_full_cta_button_bar_config_stream(self):
        # Confirms StreamBlock.get_api_representation actually reaches the
        # override on the nested rendering_condition child, not just the
        # block in isolation.
        block = CTAButtonBarBlock()
        value = block.to_python({
            'description': '',
            'actions': [],
            'config': [
                {'type': 'rendering_condition', 'value': ['role:student', 'status:verified']},
            ],
        })
        rep = block.get_api_representation(value)
        condition_entries = [entry for entry in rep['config'] if entry['type'] == 'rendering_condition']
        self.assertEqual(len(condition_entries), 1)
        self.assertEqual(condition_entries[0]['value'], 'role:student,status:verified')


class CollapsedHTMLBlockTests(TestCase):
    """A plain field block (RawHTMLBlock/EnhancedHTMLBlock) has no `collapsed`
    Meta option of its own -- only Struct/Stream/ListBlock containers respect
    it -- so this block instead attaches a Stimulus controller that drives
    the editor's existing per-block collapse toggle. This just checks the
    controller is wired onto the rendered widget; the actual collapsing is
    browser/JS behavior, verified manually (see openstax-collapse-block.js)."""

    def test_widget_carries_the_collapse_controller(self):
        # build_attrs appends to any existing data-controller value, so this
        # doesn't assume it's the only controller on the element.
        block = CollapsedHTMLBlock()
        rendered = block.field.widget.render('body-0-value', '<p>hi</p>')
        match = re.search(r'data-controller="([^"]*)"', rendered)
        self.assertIsNotNone(match, msg='no data-controller attribute rendered')
        self.assertIn('openstax-collapse-block', match.group(1).split())

    def test_widget_keeps_the_parent_blocks_own_attrs(self):
        # EnhancedHTMLBlock's own widget carries data-wagtail-html-editor and
        # rows (EnhancedHTMLWidget's default_attrs); swapping in
        # CollapsibleHTMLWidget must not drop them.
        block = CollapsedHTMLBlock()
        rendered = block.field.widget.render('body-0-value', '<p>hi</p>')
        self.assertIn('data-wagtail-html-editor="true"', rendered)
        self.assertIn('rows="10"', rendered)

    def test_media_includes_the_collapse_controller_script(self):
        block = CollapsedHTMLBlock()
        self.assertIn('pages/openstax-collapse-block.js', str(block.field.widget.media))
