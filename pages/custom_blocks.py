import copy

from django import forms

from wagtail import blocks
from wagtail.blocks import FieldBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail_ai.blocks import ai_image_block

from api.serializers import ImageSerializer
from openstax.functions import build_image_url, build_document_url
from openstax.api_fields import APIRichTextBlock
from pages.shared_blocks import CTALinkBlock, LinkInfoBlock, hex_color_block, id_config_block
from pages.table_block import TableBlock


# --- Choice constants ---
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
    ('impact', 'Impact'),
]


class LinksGroupBlock(blocks.StructBlock):
    links = blocks.ListBlock(
        LinkInfoBlock(required=False, label="Link"),
        default=[], label='Links'
    )
    config = blocks.StreamBlock([
        ('style', blocks.ChoiceBlock(choices=[
            ('button', 'Button'),
            ('text', 'Text'),
        ], help_text="Button renders the links as buttons (default); Text renders them as plain links.")),
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
        'style': {'max_num': 1},
        'color': {'max_num': 1},
        'custom_color': {'max_num': 1},
        'size': {'max_num': 1},
        'layout': {'max_num': 1},
        'analytics_label': {'max_num': 1},
    }, required=False, collapsed=True)

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
    }, required=False, collapsed=True)

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
    content = APIRichTextBlock(help_text="The quote content.")
    name = blocks.CharBlock(help_text="The name of the person or entity to attribute the quote to.")
    title = blocks.CharBlock(required=False, help_text="Additional title or label about the quotee.")
    config = blocks.StreamBlock([
        ('layout', blocks.ChoiceBlock(choices=[
            ('image-left', 'Image Left'),
            ('image-right', 'Image Right'),
            ('image-top', 'Image Top'),
            ('compact', 'Compact'),
        ], help_text='How the image and text are arranged. Compact is a small image + short text ("did you know") treatment. Default Image Left.')),
        ('accent_color', hex_color_block('Accent color for the quote. Must be hex eg: #ff0000.')),
    ], block_counts={
        'layout': {'max_num': 1},
        'accent_color': {'max_num': 1},
    }, required=False, collapsed=True)


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
            error_messages={'invalid': 'not a valid size.'}
        )),
        ('height', blocks.RegexBlock(regex=r'^[0-9]+(px|%|rem)$', required=False,
            help_text="Specifies the height of the image. Percentages are relative to the container (body or content, depending on alignment option). Must be valid css measurement. eg: 30px, 50%, 10rem. Default is the size of the image.",
            error_messages={'invalid': 'not a valid size.'}
        )),
        ('offset_vertical', blocks.RegexBlock(regex=r'^\-?[0-9]+(px|%|rem)$', required=False,
            help_text="Moves the image up or down. Percentages are relative to the image size. Must be valid css measurement. eg: 30px, 50%, 10rem. Default is -50%, which moves the image up by half its width (centering it vertically on the divider).",
            error_messages={'invalid': 'not a valid size.'}
        )),
        ('offset_horizontal', blocks.RegexBlock(regex=r'^\-?[0-9]+(px|%|rem)$', required=False,
            help_text="Moves the image left or right. Percentages are relative to the image size. Must be valid css measurement. eg: 30px, 50%, 10rem. Default is no offset, which means the image's outer edge will align with the container's edge for left and right alignment. or it'll be perfectly centered for centered alignment.",
            error_messages={'invalid': 'not a valid size.'}
        ))
    ], block_counts={
        'alignment': {'max_num': 1},
        'width': {'max_num': 1},
        'height': {'max_num': 1},
        'offset_vertical': {'max_num': 1},
        'offset_horizontal': {'max_num': 1},
    }, required=False, collapsed=True)


@ai_image_block()
class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    alt_text = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    alignment = ImageFormatChoiceBlock()
    identifier = blocks.CharBlock(required=False, help_text="Used by the frontend for Google Analytics.")


class ColumnBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    content = APIRichTextBlock(required=False)
    image = ImageBlock(required=False, help_text='Callout boxes 940x400, Home page boxes 1464x640')
    document = DocumentChooserBlock(required=False)
    cta = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = 'placeholder'


class FAQBlock(blocks.StructBlock):
    question = APIRichTextBlock(required=True, help_text='The visible text of the question (does not collapse).')
    slug = blocks.CharBlock(required=True, help_text='Not visible to user, must be unique in this FAQ.')
    answer = APIRichTextBlock(required=True, help_text='The answer to the question, is hidden until the question is expanded.')
    document = DocumentChooserBlock(required=False, help_text='Not sure this does anything.')
    content = blocks.StreamBlock([
        ('table', TableBlock()),
        ('image', blocks.StructBlock([
            ('image', APIImageChooserBlock(required=True)),
            ('alt_text', blocks.CharBlock(required=False)),
        ], label='Image')),
        ('text', APIRichTextBlock()),
    ], required=False, collapsed=True, label='Additional content',
        help_text='Optional table, image, or extra text shown as part of the answer.')

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
    description = APIRichTextBlock(required=True)

    class Meta:
        icon = 'form'


class CardImageBlock(blocks.StructBlock):
    icon = APIImageChooserBlock(required=False)
    title = blocks.CharBlock(required=True)
    description = APIRichTextBlock(required=True)

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
    testimonial = APIRichTextBlock(required=True)

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
                'cover': build_document_url(value['cover'].url) if value['cover'] else None,
                'title': value['title'],
            }

class BookBlock(blocks.PageChooserBlock):
    def __init__(self, *args, **kwargs):
        kwargs['page_type'] = ['books.Book']
        kwargs['label'] = kwargs.get('label', 'Book')
        super().__init__(*args, **kwargs)

    def bulk_to_python(self, values):
        # get_api_representation (via get_book_data) touches book_subjects,
        # k12book_subjects, book_categories, cover_image/cover/title_image/
        # banner_image/pdf, and the faculty/student resource flags for every
        # book in a Book Block or Book List — resolving those relations one
        # book at a time turns an N-book block into 10+N DB queries. Fetch
        # them all at once.
        from books.models import prefetch_book_resources
        queryset = prefetch_book_resources(
            self.model_class.objects
            .select_related('cover_image', 'cover', 'title_image', 'banner_image', 'pdf')
            .prefetch_related('book_subjects__subject', 'k12book_subjects__subject', 'book_categories__category')
        )
        objects = queryset.in_bulk(values)
        seen_ids = set()
        result = []
        for id in values:
            obj = objects.get(id)
            if obj is not None and id in seen_ids:
                obj = copy.copy(obj)
            result.append(obj)
            seen_ids.add(id)
        return result

    def get_api_representation(self, value, context=None):
        from books.models import get_book_data
        if value:
            return get_book_data(value)


class PersonTagChooserBlock(SnippetChooserBlock):
    """Serializes a PersonTag snippet inline as {id, name, slug} so the renderer
    needs no extra fetch (same technique as books.SharedContentChooserBlock)."""
    def get_api_representation(self, value, context=None):
        if value:
            return {'id': value.id, 'name': value.name, 'slug': value.slug}
        return None


PERSON_LINK_TYPE_CHOICES = [
    ('linkedin', 'LinkedIn'),
    ('orcid', 'ORCID'),
    ('website', 'Website'),
    ('email', 'Email'),
    ('scholar', 'Google Scholar'),
    ('x', 'X'),
]


class PersonLinkBlock(blocks.StructBlock):
    type = blocks.ChoiceBlock(choices=PERSON_LINK_TYPE_CHOICES, required=True,
        help_text='Determines the icon shown for this link.')
    # CharBlock (not URLBlock) so the "Email" type can hold a mailto: link or a
    # bare address — URLBlock only allows http/https/ftp and would reject both.
    url = blocks.CharBlock(required=True,
        help_text='Full URL, or for the Email type a mailto: link or email address.')

    class Meta:
        label = 'Link'


class PersonBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False,
        help_text='Optional title shown above the grid.')
    people = blocks.ListBlock(blocks.StructBlock([
        ('name', blocks.CharBlock(required=True)),
        ('title', blocks.CharBlock(required=False, help_text='Role, e.g. "Director of Research".')),
        ('image', APIImageChooserBlock(required=False)),
        ('short_bio', blocks.TextBlock(required=False, help_text='Shown on the card.')),
        ('full_bio', APIRichTextBlock(required=False,
            help_text='If set, the card becomes clickable and opens an expanded modal.')),
        ('links', blocks.ListBlock(PersonLinkBlock(), default=[], required=False)),
        ('tags', blocks.ListBlock(PersonTagChooserBlock('pages.PersonTag'), default=[], required=False)),
    ]))
    config = blocks.StreamBlock([
        ('card_columns', blocks.IntegerBlock(min_value=1, max_value=6, help_text='Number of columns for the grid. default auto.')),
        ('card_style', blocks.ChoiceBlock(choices=CARDS_STYLE_CHOICES, help_text='The border style of the cards. default borderless.')),
        ('card_size', blocks.IntegerBlock(min_value=0, help_text='Width of individual cards. default 27.')),
        ('accent_colors', blocks.RegexBlock(
            regex=r'^#[0-9a-fA-F]{6}(\s*,\s*#[0-9a-fA-F]{6})*$', required=False,
            label='Accent Colors',
            help_text='Comma-separated hex colors for a card accent, cycled per card. eg: #ff0000,#00ff00,#0000ff.',
            error_messages={'invalid': 'Must be comma-separated hex colors. eg: #ff0000,#00ff00.'},
        )),
        ('divider_colors', blocks.RegexBlock(
            regex=r'^#[0-9a-fA-F]{6}(\s*,\s*#[0-9a-fA-F]{6})*$', required=False,
            label='Divider Colors',
            help_text='Comma-separated hex colors for card divider lines, cycled per card. eg: #ff0000,#00ff00.',
            error_messages={'invalid': 'Must be comma-separated hex colors. eg: #ff0000,#00ff00.'},
        )),
        ('background_color', hex_color_block('Background color for the cards. Must be hex eg: #ff0000.')),
        ('border_size', blocks.IntegerBlock(min_value=0, help_text='Border width in px.')),
        ('id', id_config_block()),
    ], block_counts={
        'card_columns': {'max_num': 1},
        'card_style': {'max_num': 1},
        'card_size': {'max_num': 1},
        'accent_colors': {'max_num': 1},
        'divider_colors': {'max_num': 1},
        'background_color': {'max_num': 1},
        'border_size': {'max_num': 1},
        'id': {'max_num': 1},
    }, required=False, collapsed=True)

    class Meta:
        label = 'People'
        icon = 'group'
