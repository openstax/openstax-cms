from django import forms
import json
from django.utils.functional import cached_property

from wagtail import blocks
from wagtail.blocks import FieldBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail_ai.blocks import ai_image_block
from wagtail_color_panel.blocks import NativeColorBlock
from wagtail_color_panel.widgets import ColorInputWidget, ColorInputWidgetAdapter
from wagtail.admin.telepath import register

from api.serializers import ImageSerializer
from openstax.functions import build_image_url, build_document_url
from wagtail.rich_text import expand_db_html
from books.models import get_book_data


# --- Choice constants ---
GRADIENT_DIRECTION_CHOICES = [
    ('to_right', 'To Right'),
    ('to_left', 'To Left'),
    ('to_top', 'To Top'),
    ('to_bottom', 'To Bottom'),
    ('to_top_right', 'To Top Right'),
    ('to_top_left', 'To Top Left'),
    ('to_bottom_right', 'To Bottom Right'),
    ('to_bottom_left', 'To Bottom Left'),
]

TEXT_ALIGNMENT_CHOICES = [
    ('left', 'Left'),
    ('center', 'Center'),
    ('right', 'Right'),
]

FLEX_CHOICES = [
    ('flex', 'Flex'),
    ('flex_grow', 'Flex Grow'),
    ('flex_shrink', 'Flex Shrink'),
]

CARDS_STYLE_CHOICES = [
    ('rounded', 'Rounded'),
    ('square', 'Square'),
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
        # Return an empty STRING (not None) for blank values: the package's
        # color-input template renders the native chip as value="{{ widget.value }}"
        # with no None-guard, and Django renders Python None as the string "None"
        # — which the <input type="color"> rejects. value="" harmlessly becomes
        # #000000 instead.
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
        # Stimulus value: the controller reads this as `this.paletteValue`.
        field.widget.attrs['data-openstax-color-swatches-palette-value'] = json.dumps(self.brand_colors)
        return field

    def value_for_form(self, value):
        # An empty color is sometimes stored as the literal string "None", which
        # the native <input type="color"> rejects. Coerce it (and any non-hex
        # junk) to blank before it reaches the widget; valid hex passes through.
        # Also cleans a stored "None" back to blank on the next save.
        if value is None:
            return value
        text = str(value).strip()
        if text == '' or text.lower() == 'none':
            return ''
        return super().value_for_form(value)


# --- Helper factories ---
def hex_color_block(help_text):
    return OpenStaxColorBlock(help_text=help_text)


def gradient_config_options():
    return [
        ('gradient_color', hex_color_block('Sets the gradient end color. Must be hex eg: #ff0000.')),
        ('gradient_direction', blocks.ChoiceBlock(
            choices=GRADIENT_DIRECTION_CHOICES,
            help_text='Direction of the gradient. Default to_right.',
        )),
    ]


def gradient_block_counts():
    return {
        'gradient_color': {'max_num': 1},
        'gradient_direction': {'max_num': 1},
    }


def id_config_block():
    return blocks.RegexBlock(
        regex=r'[a-zA-Z0-9\-_]',
        help_text='HTML id of this element. not visible to users, but is visible in urls and is used to link to a certain part of the page with an anchor link. eg: cool_section',
        error_mssages={'invalid': 'not a valid id.'}
    )


class APIRichTextBlock(blocks.RichTextBlock):
    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        return expand_db_html(representation)

    class Meta:
        icon = 'doc-full'


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
                return {
                    'value': child.value.url_path,
                    'type': child.block_type,
                }
            elif child.block_type == 'anchor':
                return {
                    'value': "#{anchor}".format(anchor=child.value),
                    'type': child.block_type,
                }
            else:
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
    }, required=False)

    class Meta:
        icon = 'placeholder'
        label = "Call to Action"


class LinksGroupBlock(blocks.StructBlock):
    links = blocks.ListBlock(
        LinkInfoBlock(required=False, label="Link"),
        default=[], label='Links'
    )
    config = blocks.StreamBlock([
        ('color', blocks.ChoiceBlock(choices=[
            ('white', 'White'),
            ('blue', 'Blue'),
            ('deep-green', 'Deep Green'),
        ], help_text="The color of the link buttons. Default white.")),
        ('custom_color', hex_color_block('Custom color for the links. Must be hex eg: #ff0000.')),
        ('size', blocks.ChoiceBlock(choices=[
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large'),
        ], help_text='Size of the links. Default medium.')),
        ('layout', blocks.ChoiceBlock(choices=[
            ('horizontal', 'Horizontal'),
            ('vertical', 'Vertical'),
        ], help_text='Layout direction of the links. Default horizontal.')),
        ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this group.')),
    ], block_counts={
        'color': {'max_num': 1},
        'custom_color': {'max_num': 1},
        'size': {'max_num': 1},
        'layout': {'max_num': 1},
        'analytics_label': {'max_num': 1},
    }, required=False)

    class Meta:
        icon = 'placeholder'
        label = "Links Group"

class CTAButtonBarBlock(blocks.StructBlock):
    description = blocks.CharBlock(required=False, help_text='Optional description text displayed alongside the buttons.')
    actions = blocks.ListBlock(
        CTALinkBlock(required=False, label="Button"),
        default=[], max_num=2, label='Actions'
    )
    config = blocks.StreamBlock([
        ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this group.')),
        ('layout', blocks.ChoiceBlock(choices=[
            ('inline', 'Inline'),
        ], help_text='Layout of the buttons. Inline places description and buttons side-by-side.')),
        ('rendering_condition', blocks.CharBlock(required=False, help_text='Condition that determines if this block should render. eg: defined by the frontend.')),
    ], block_counts={
        'analytics_label': {'max_num': 1},
        'layout': {'max_num': 1},
        'rendering_condition': {'max_num': 1},
    }, required=False)

    class Meta:
        icon = 'placeholder'
        label = "Calls to Action"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(required=False, choices=(
        ('left', 'Wrap left'),
        ('right', 'Wrap right'),
        ('mid', 'Mid width'),
        ('full', 'Full width'),
    ))


class APIImageChooserBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        try:
            return ImageSerializer(context=context).to_representation(value)
        except AttributeError:
            return None

class QuoteBlock(StructBlock):
    image = APIImageChooserBlock()
    content = blocks.RichTextBlock(help_text="The quote content.")
    name = blocks.CharBlock(help_text="The name of the person or entity to attribute the quote to.")
    title = blocks.CharBlock(required=False, help_text="Additional title or label about the quotee.")
    config = blocks.StreamBlock([
        ('accent_color', hex_color_block('Accent color for the quote. Must be hex eg: #ff0000.')),
    ], block_counts={
        'accent_color': {'max_num': 1},
    }, required=False)


class DividerBlock(StructBlock):
    image = APIImageChooserBlock()
    config = blocks.StreamBlock([
        ('alignment', blocks.ChoiceBlock(choices=[
            ('center', 'Center'),
            ('content_left', 'Left side of content.'),
            ('content_right', 'Right side of content.'),
            ('body_left', 'Left side of window.'),
            ('body_right', 'Right side of window.'),
        ], default='center', help_text='Sets the horizontal alignment of the image. can be further customized with the "Offset..." configurations. Default is Left side of window.')),
        ('width', blocks.RegexBlock(regex=r'^[0-9]+(px|%|rem)$', required=False,
            help_text="Specifies the width of the image. Percentages are relative to the container (body or content, depending on alignment option). Must be valid css measurement. eg: 30px, 50%, 10rem. Default is the size of the image.",
            error_mssages={'invalid': 'not a valid size.'}
        )),
        ('height', blocks.RegexBlock(regex=r'^[0-9]+(px|%|rem)$', required=False,
            help_text="Specifies the height of the image. Percentages are relative to the container (body or content, depending on alignment option). Must be valid css measurement. eg: 30px, 50%, 10rem. Default is the size of the image.",
            error_mssages={'invalid': 'not a valid size.'}
        )),
        ('offset_vertical', blocks.RegexBlock(regex=r'^\-?[0-9]+(px|%|rem)$', required=False,
            help_text="Moves the image up or down. Percentages are relative to the image size. Must be valid css measurement. eg: 30px, 50%, 10rem. Default is -50%, which moves the image up by half its width (centering it vertically on the divider).",
            error_mssages={'invalid': 'not a valid size.'}
        )),
        ('offset_horizontal', blocks.RegexBlock(regex=r'^\-?[0-9]+(px|%|rem)$', required=False,
            help_text="Moves the image left or right. Percentages are relative to the image size. Must be valid css measurement. eg: 30px, 50%, 10rem. Default is no offset, which means the image's outer edge will align with the container's edge for left and right alignment. or it'll be perfectly centered for centered alignment.",
            error_mssages={'invalid': 'not a valid size.'}
        ))
    ], block_counts={
        'alignment': {'max_num': 1},
        'width': {'max_num': 1},
        'height': {'max_num': 1},
        'offset_vertical': {'max_num': 1},
        'offset_horizontal': {'max_num': 1},
    }, required=False)


@ai_image_block()
class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    alt_text = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    alignment = ImageFormatChoiceBlock()
    identifier = blocks.CharBlock(required=False, help_text="Used by the frontend for Google Analytics.")


class ColumnBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    content = blocks.RichTextBlock(required=False)
    image = ImageBlock(required=False, help_text='Callout boxes 940x400, Home page boxes 1464x640')
    document = DocumentChooserBlock(required=False)
    cta = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = 'placeholder'


class FAQBlock(blocks.StructBlock):
    question = blocks.RichTextBlock(required=True, help_text='The visible text of the question (does not collapse).')
    slug = blocks.CharBlock(required=True, help_text='Not visible to user, must be unique in this FAQ.')
    answer = blocks.RichTextBlock(required=True, help_text='The answer to the question, is hidden until the question is expanded.')
    document = DocumentChooserBlock(required=False, help_text='Not sure this does anything.')

    class Meta:
        icon = 'bars'


class BookProviderBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    blurb = blocks.TextBlock(required=False)
    icon = ImageChooserBlock()
    cta = blocks.CharBlock()
    url = blocks.URLBlock()
    canadian = blocks.BooleanBlock(required=False)

    class Meta:
        icon = 'document'

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'name': value['name'],
                'blurb': value['blurb'],
                'icon': build_image_url(value['icon']),
                'cta': value['cta'],
                'url': value['url'],
                'canadian': value['canadian']
            }


class CardBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    description = blocks.RichTextBlock(required=True)

    class Meta:
        icon = 'form'


class CardImageBlock(blocks.StructBlock):
    icon = APIImageChooserBlock(required=False)
    title = blocks.CharBlock(required=True)
    description = blocks.RichTextBlock(required=True)

    class Meta:
        icon = 'image'


class StoryBlock(blocks.StructBlock):
    image = APIImageChooserBlock(required=False)
    story_text = blocks.TextBlock(required=False)
    linked_story = blocks.PageChooserBlock(page_type=['pages.ImpactStory', 'news.NewsArticle'])
    embedded_video = blocks.RawHTMLBlock(required=False)

    class Meta:
        icon = 'openquote'


class TutorAdBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    image = APIImageChooserBlock()
    ad_html = blocks.TextBlock()
    link_text = blocks.CharBlock()
    link_href = blocks.URLBlock()

    class Meta:
        icon = 'placeholder'
        max_num = 1


class AboutOpenStaxBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    image = APIImageChooserBlock()
    os_text = blocks.TextBlock()
    link_text = blocks.CharBlock()
    link_href = blocks.URLBlock()

    class Meta:
        icon = 'placeholder'
        max_num = 1


class InfoBoxBlock(blocks.StructBlock):
    image = APIImageChooserBlock()
    heading = blocks.CharBlock()
    text = blocks.CharBlock()

    class Meta:
        icon = 'placeholder'


class TestimonialBlock(blocks.StructBlock):
    author_icon = APIImageChooserBlock(required=False)
    author_name = blocks.CharBlock(required=True)
    author_title = blocks.CharBlock(required=True)
    testimonial = blocks.RichTextBlock(required=True)

    class Meta:
        author_icon = 'image'
        max_num = 4


class AllyLogoBlock(blocks.StructBlock):
    image = APIImageChooserBlock()

    class Meta:
        icon = 'placeholder'


class AssignableBookBlock(blocks.StructBlock):
    cover = DocumentChooserBlock(required=False)
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = 'image'

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'cover': build_document_url(value['cover'].url),
                'title': value['title'],
            }

class BookBlock(blocks.PageChooserBlock):
    def __init__(self, *args, **kwargs):
        kwargs['page_type'] = ['books.Book']
        kwargs['label'] = kwargs.get('label', 'Book')
        super().__init__(*args, **kwargs)

    def get_api_representation(self, value, context=None):
        if value:
            return get_book_data(value)
