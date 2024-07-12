from django import forms

from wagtail import blocks
from wagtail.blocks import FieldBlock, StructBlock, StructValue
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

from api.serializers import ImageSerializer
from openstax.functions import build_image_url, build_document_url


class APIRichTextBlock(blocks.RichTextBlock):
    def get_api_representation(self, value, context=None):
        return value.source

    class Meta:
        icon = 'doc-full'

class LinkStructValue(StructValue):
    def url(self):
        if self['external']:
            return self['external']
        elif self['internal']:
            return self['internal']
        elif self['document']:
            return build_document_url(self['document'].url)
        else:
            return None

    def text(self):
        return self['text']

    def link_aria_label(self):
        return self['link_aria_label']

    def __bool__(self):
        return bool(self.url())

class LinkBlock(blocks.StreamBlock):
    external = blocks.URLBlock(required=False)
    internal = blocks.PageChooserBlock(required=False)
    document = DocumentChooserBlock(required=False)

    class Meta:
        icon = 'link'
        max_num = 1

class CTAButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)
    link_aria_label = blocks.CharBlock(required=False)

    class Meta:
        icon = 'placeholder'
        label = "CTA Button"
        value_class = LinkStructValue

class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(required=False, choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),))


class ImageStructValue(StructValue):
    def image(self):
        return build_image_url(self['image'])

    def alt_text(self):
        return self['alt_text']

    def alignment(self):
        return self['alignment']

    def cta(self):
        return self['cta']

# Use this block to return the path in the page API, does not support alt_text and alignment
class APIImageBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    alt_text = blocks.CharBlock(required=False)
    alignment = ImageFormatChoiceBlock(required=False)
    cta = CTAButtonBlock(required=False, label="CTA")

    def get_api_representation(self, value, context=None):
        try:
            return ImageSerializer(context=context).to_representation(value)
        except AttributeError:
            return None

    class Meta:
        icon = 'image'
        # value_class = ImageStructValue


# TODO: deprecate this block and move to the APIImageBlock
class APIImageChooserBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        try:
            return ImageSerializer(context=context).to_representation(value)
        except AttributeError:
            return None


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
    question = blocks.RichTextBlock(required=True)
    slug = blocks.CharBlock(required=True)
    answer = blocks.RichTextBlock(required=True)
    document = DocumentChooserBlock(required=False)

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
    linked_story = blocks.PageChooserBlock(target_model='pages.ImpactStory')
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


class CardsBlock(blocks.StructBlock):
    STYLE_CHOICES = [
        ('rounded', 'Rounded'),
        ('square', 'Square'),
    ]
    text = APIRichTextBlock(required=False)
    cta = CTAButtonBlock(required=False)
    image = APIImageBlock(required=False)
    style = blocks.ChoiceBlock(choices=STYLE_CHOICES, default='rounded')

    class Meta:
        icon = 'form'
