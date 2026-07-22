import json

from django import forms
from django.utils.functional import cached_property

from wagtail import blocks
from wagtail.admin.telepath import register
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail_color_panel.blocks import NativeColorBlock
from wagtail_color_panel.widgets import ColorInputWidget, ColorInputWidgetAdapter
from wagtail_html_editor.blocks import EnhancedHTMLBlock
from wagtail_html_editor.telepath import EnhancedHTMLWidgetAdapter
from wagtail_html_editor.widgets import EnhancedHTMLWidget

# Leaf module: color/link/id primitives shared by pages/custom_blocks.py,
# pages/models/*, and pages/table_block.py.
# Keep this module free of imports from pages.custom_blocks or pages.table_block
# to avoid circular-import issues.

GRADIENT_DIRECTION_CHOICES = [
    ('to right', 'To Right'),
    ('to left', 'To Left'),
    ('to top', 'To Top'),
    ('to bottom', 'To Bottom'),
    ('to top right', 'To Top Right'),
    ('to top left', 'To Top Left'),
    ('to bottom right', 'To Bottom Right'),
    ('to bottom left', 'To Bottom Left'),
]

OPENSTAX_BRAND_COLORS = [
    {'label': 'Green Dark', 'value': '#204B00'},
    {'label': 'Green Warm', 'value': '#538E1D'},
    {'label': 'Green Bright', 'value': '#76AE43'},
    {'label': 'Green Light', 'value': '#F5FFEC'},
    {'label': 'Teal Dark', 'value': '#0A5B50'},
    {'label': 'Teal Warm', 'value': '#0C9372'},
    {'label': 'Teal Bright', 'value': '#00CCA0'},
    {'label': 'Teal Light', 'value': '#F0FEFE'},
    {'label': 'Blue Dark', 'value': '#002E6D'},
    {'label': 'Blue Warm', 'value': '#026AA1'},
    {'label': 'Blue Bright', 'value': '#00C1DE'},
    {'label': 'Blue Light', 'value': '#F7FCFF'},
    {'label': 'Pink Dark', 'value': '#461347'},
    {'label': 'Pink Warm', 'value': '#9A2959'},
    {'label': 'Pink Bright', 'value': '#B72567'},
    {'label': 'Pink Light', 'value': '#FFF0F7'},
    {'label': 'Orange Dark', 'value': '#D4450C'},
    {'label': 'Orange Warm', 'value': '#EF6428'},
    {'label': 'Orange Bright', 'value': '#FF8753'},
    {'label': 'Orange Light', 'value': '#FFF5F0'},
    {'label': 'Yellow Dark', 'value': '#FDBD3E'},
    {'label': 'Yellow Warm', 'value': '#F4D019'},
    {'label': 'Yellow Bright', 'value': '#FFE665'},
    {'label': 'Yellow Light', 'value': '#FFFCEF'},
    {'label': 'Gray Dark', 'value': '#424242'},
    {'label': 'Gray Warm', 'value': '#6A6A6A'},
    {'label': 'Gray Bright', 'value': '#9A9A9B'},
    {'label': 'Gray Light', 'value': '#F5F5F5'},
]


class OpenStaxColorInputWidget(ColorInputWidget):
    """ColorInputWidget extended with the OpenStax brand-swatch picker.

    - ``format_value`` renders empty / invalid values as blank rather than the
      literal string "None" (the native <input type="color"> rejects non-#rrggbb
      values with a browser console warning; blank harmlessly becomes #000000).
    - ``build_attrs`` attaches the ``openstax-color-swatches`` Stimulus controller
      alongside the package's own ``color-input`` controller, so the swatch panel
      auto-initialises whenever the field enters the DOM — including
      dynamically-added StreamField blocks — with no MutationObserver.
    - ``media`` ships the swatch CSS/JS, loaded only when a colour field is on the
      page (the idiomatic Wagtail mechanism; ``insert_editor_css`` is not rendered
      in Wagtail 7.4)."""

    def format_value(self, value):
        if value is None:
            return ''
        text = str(value).strip()
        if text == '' or text.lower() == 'none':
            return ''
        return super().format_value(value)

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        controllers = (attrs.get('data-controller') or '').split()
        if 'openstax-color-swatches' not in controllers:
            controllers.append('openstax-color-swatches')
        attrs['data-controller'] = ' '.join(controllers)
        return attrs

    @property
    def media(self):
        return super().media + forms.Media(
            css={'all': ['pages/openstax-color-swatches.css']},
            js=['pages/openstax-color-swatches.js'],
        )


class OpenStaxColorInputWidgetAdapter(ColorInputWidgetAdapter):
    # Reuses the package's JS constructor + Media; telepath needs an adapter
    # registered against this exact widget subclass.
    pass


register(OpenStaxColorInputWidgetAdapter(), OpenStaxColorInputWidget)


class OpenStaxColorBlock(NativeColorBlock):
    """Native color picker with OpenStax brand swatches for quick selection."""

    def __init__(self, required=True, help_text=None, validators=(), brand_colors=None, **kwargs):
        self.brand_colors = brand_colors or OPENSTAX_BRAND_COLORS
        super().__init__(required=required, help_text=help_text, validators=validators, **kwargs)

    @cached_property
    def field(self):
        field = super().field
        field.widget = OpenStaxColorInputWidget()
        field.widget.attrs['data-openstax-color-swatches-palette-value'] = json.dumps(self.brand_colors)
        return field

    def value_for_form(self, value):
        if value is None:
            return value
        text = str(value).strip()
        if text == '' or text.lower() == 'none':
            return ''
        return super().value_for_form(value)


def hex_color_block(help_text):
    return OpenStaxColorBlock(help_text=help_text)


class CollapsibleHTMLWidget(EnhancedHTMLWidget):
    """EnhancedHTMLWidget with the openstax-collapse-block Stimulus controller
    attached, so the block starts collapsed in the StreamField editor.

    A plain field widget has no `collapsed` Meta option of its own (only
    Struct/Stream/ListBlock containers respect it), so this drives the
    editor's existing per-block collapse toggle directly instead — see
    openstax-collapse-block.js. HTML blocks are usually long and rarely
    need editing once written, so hiding them by default keeps the block
    list scannable."""

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        controllers = (attrs.get('data-controller') or '').split()
        if 'openstax-collapse-block' not in controllers:
            controllers.append('openstax-collapse-block')
        attrs['data-controller'] = ' '.join(controllers)
        return attrs

    @property
    def media(self):
        return super().media + forms.Media(js=['pages/openstax-collapse-block.js'])


class CollapsibleHTMLWidgetAdapter(EnhancedHTMLWidgetAdapter):
    # Reuses the package's JS constructor + rendering; telepath needs an
    # adapter registered against this exact widget subclass.
    pass


register(CollapsibleHTMLWidgetAdapter(), CollapsibleHTMLWidget)


class CollapsedHTMLBlock(EnhancedHTMLBlock):
    """EnhancedHTMLBlock using CollapsibleHTMLWidget in place of the
    package's default widget, so it starts collapsed in the editor."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Preserve whatever attrs EnhancedHTMLBlock's own widget ended up
        # with, rather than dropping them by constructing a bare replacement.
        self.field.widget = CollapsibleHTMLWidget(attrs=dict(self.field.widget.attrs))


def gradient_config_options():
    return [
        ('gradient_color', hex_color_block('Sets the gradient end color. Must be hex eg: #ff0000.')),
        ('gradient_direction', blocks.ChoiceBlock(
            choices=GRADIENT_DIRECTION_CHOICES,
            help_text='Direction of the gradient. Default to right.',
        )),
    ]


def gradient_block_counts():
    return {
        'gradient_color': {'max_num': 1},
        'gradient_direction': {'max_num': 1},
    }


def id_config_block():
    return blocks.RegexBlock(
        regex=r'^[a-zA-Z0-9_-]+$',
        help_text='HTML id of this element. not visible to users, but is visible in urls and is used to link to a certain part of the page with an anchor link. eg: cool_section',
        error_messages={'invalid': 'not a valid id.'}
    )


class LinkBlock(blocks.StreamBlock):
    external = blocks.URLBlock(required=False, help_text='External links are full urls that can go anywhere')
    internal = blocks.PageChooserBlock(required=False)
    document = DocumentChooserBlock(required=False)
    anchor = blocks.CharBlock(required=False, help_text='Anchor links reference the ID of an element on the page, and scroll the page there.')

    class Meta:
        icon = 'link'
        max_num = 1

    def get_api_representation(self, value, context=None):
        for child in value:
            if child.block_type == 'document':
                if child.value is None:
                    return None
                return {
                    'value': child.value.url,
                    'type': child.block_type,
                    'metadata': child.value.content_type,
                }
            elif child.block_type == 'external':
                return {
                    'value': child.block.get_prep_value(child.value),
                    'type': child.block_type,
                }
            elif child.block_type == 'internal':
                if child.value is None:
                    return None
                page = child.value.specific
                return {
                    'value': page.url or page.url_path,
                    'type': child.block_type,
                }
            elif child.block_type == 'anchor':
                return {
                    'value': "#{anchor}".format(anchor=child.value),
                    'type': child.block_type,
                }
            else:
                return None
        return None


class LinkInfoBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text='Visible text of the link or button.')
    aria_label = blocks.CharBlock(required=False, help_text='Accessible label for the link or button. if provided, must begin with the visible text.')
    target = LinkBlock(required=True)

    class Meta:
        icon = 'placeholder'
        label = "Link"


class CTALinkBlock(LinkInfoBlock):
    text = blocks.CharBlock(required=True, help_text='Visible text of the link or button.')
    aria_label = blocks.CharBlock(required=False, help_text='Accessible label for the link or button. if provided, must begin with the visible text.')
    target = LinkBlock(required=True)
    config = blocks.StreamBlock([
        ('style', blocks.ChoiceBlock(choices=[
            ('orange', 'Orange'),
            ('white', 'White'),
            ('blue_outline', 'Blue Outline'),
            ('deep_green_outline', 'Deep Green Outline'),
        ], help_text='Specifies the button style. Default unspecified, meaning the first button in the block is orange and the second is white.')),
        ('custom_color', hex_color_block('Custom color for the button. Must be hex eg: #ff0000.')),
    ], block_counts={
        'style': {'max_num': 1},
        'custom_color': {'max_num': 1},
    }, required=False, collapsed=True)

    class Meta:
        icon = 'placeholder'
        label = "Call to Action"
