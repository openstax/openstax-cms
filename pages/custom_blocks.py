from django import forms

from wagtail import blocks
from wagtail.blocks import FieldBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

from api.serializers import ImageSerializer
from openstax.functions import build_image_url, build_document_url
from wagtail.rich_text import expand_db_html


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
    ], block_counts={
        'style': {'max_num': 1},
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
        ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this group.')),
    ], block_counts={
        'color': {'max_num': 1},
        'analytics_label': {'max_num': 1},
    }, required=False)

    class Meta:
        icon = 'placeholder'
        label = "Links Group"

class CTAButtonBarBlock(blocks.StructBlock):
    actions = blocks.ListBlock(
        CTALinkBlock(required=False, label="Button"),
        default=[], max_num=2, label='Actions'
    )
    config = blocks.StreamBlock([
        ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this group.')),
    ], block_counts={
        'analytics_label': {'max_num': 1},
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
    title = blocks.CharBlock(requred=False, help_text="Additional title or label about the quotee.")

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
