import json
from django import forms
from django.db import models
from django.http.response import JsonResponse
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel,
                                                MultiFieldPanel,
                                                PageChooserPanel,
                                                StreamFieldPanel)
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks import FieldBlock, RawHTMLBlock, StructBlock
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from openstax.functions import build_image_url


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(
        choices=(('normal', 'Normal'), ('full', 'Full width'),))


class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class StrategicAdvisors(LinkFields):
    name = models.CharField(max_length=255, help_text="Strategic Advisor Name")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_advisor_image(self):
        return build_image_url(self.image)

    advisor_image = property(get_advisor_image)

    description = models.TextField()

    api_fields = ('name', 'advisor_image', 'description', )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('image'),
        FieldPanel('description'),
    ]


class OpenStaxTeam(LinkFields):
    name = models.CharField(max_length=255, help_text="Team Member Name")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_team_member_image(self):
        return build_image_url(self.image)
    team_member_image = property(get_team_member_image)

    position = models.CharField(max_length=255)
    description = models.TextField()

    api_fields = ('name', 'team_member_image', 'position', 'description', )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('image'),
        FieldPanel('position'),
        FieldPanel('description'),
    ]


class PersonBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True)
    position = blocks.CharBlock(required=True)
    photo = ImageBlock()
    biography = models.TextField()

    class Meta:
        icon = 'user'


class QuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock()
    author = blocks.CharBlock()


class ColumnBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    content = blocks.RichTextBlock(required=False)
    image = ImageBlock(required=False)
    document = DocumentChooserBlock(required=False)
    cta = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = 'placeholder'


class AboutUsStrategicAdvisors(Orderable, StrategicAdvisors):
    page = ParentalKey('pages.AboutUs', related_name='strategic_advisors')


class AboutUsOpenStaxTeam(Orderable, OpenStaxTeam):
    page = ParentalKey('pages.AboutUs', related_name='openstax_team')


class AboutUs(Page):
    tagline = models.CharField(max_length=255)
    intro_heading = models.CharField(max_length=255)
    intro_paragraph = RichTextField()
    our_team_heading = models.CharField(max_length=255)

    api_fields = (
        'tagline',
        'intro_heading',
        'intro_paragraph',
        'our_team_heading',
        'openstax_team',
        'strategic_advisors',
        'slug',
        'seo_title',
        'search_description',)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tagline'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_paragraph'),
        FieldPanel('our_team_heading'),
        InlinePanel('openstax_team', label="OpenStax Team"),
        InlinePanel('strategic_advisors', label="Strategic Advisors"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class Allies(LinkFields):
    heading = models.CharField(max_length=255)
    description = RichTextField()
    link_url = models.URLField(blank=True, help_text="Call to Action Link")
    link_text = models.CharField(
        max_length=255, help_text="Call to Action Text")

    api_fields = ('heading', 'description', 'link_url', 'link_text', )

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('link_url'),
        FieldPanel('link_text'),
    ]


class Quote(models.Model):
    IMAGE_ALIGNMENT_CHOICES = (
        ('L', 'left'),
        ('R', 'right'),
        ('F', 'full'),
    )
    quote_text = RichTextField()

    quote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_quote_image(self):
        return build_image_url(self.quote_image)
    quote_image_url = property(get_quote_image)

    quote_image_alignment = models.CharField(max_length=1,
                                             choices=IMAGE_ALIGNMENT_CHOICES,
                                             blank=True,
                                             null=True)
    quote_link = models.URLField(blank=True, null=True)
    quote_link_text = models.CharField(max_length=255, blank=True, null=True)

    api_fields = (
        'quote_text',
        'quote_image_url',
        'get_quote_image_alignment_display',
        'quote_link',
        'quote_link_text',
    )

    panels = [
        FieldPanel('quote_text'),
        ImageChooserPanel('quote_image'),
        FieldPanel('quote_image_alignment'),
        FieldPanel('quote_link'),
        FieldPanel('quote_link_text'),
    ]


# Home Page
class HomePage(Page):
    row_1 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])
    row_2 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])
    row_3 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])
    row_4 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])
    row_5 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])

    api_fields = (
        'title',
        'row_1',
        'row_2',
        'row_3',
        'row_4',
        'row_5',
        'slug',
        'seo_title',
        'search_description',)

    class Meta:
        verbose_name = "Home Page"

    content_panels = [
        FieldPanel('title', classname="full title"),
        StreamFieldPanel('row_1'),
        StreamFieldPanel('row_2'),
        StreamFieldPanel('row_3'),
        StreamFieldPanel('row_4'),
        StreamFieldPanel('row_5'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    # we are controlling what types of pages are allowed under a homepage
    # if a new page type is created, it needs to be added here to show up in
    # the admin
    subpage_types = [
        'pages.HigherEducation',
        'pages.ContactUs',
        'pages.AboutUs',
        'pages.GeneralPage',
        'pages.EcosystemAllies',
        'books.BookIndex',
        'news.NewsIndex',
        'allies.Ally',
    ]


class HigherEducationAllies(Orderable, Allies):
    page = ParentalKey(
        'pages.HigherEducation', related_name='higher_education_allies')


class HigherEducation(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()

    row_1 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])

    get_started_heading = models.CharField(max_length=255)

    get_started_step_1_heading = models.CharField(max_length=255)
    get_started_step_1_description = RichTextField()
    get_started_step_1_cta = models.CharField(max_length=255)

    get_started_step_2_heading = models.CharField(max_length=255)
    get_started_step_2_description = RichTextField()
    get_started_step_2_cta = models.CharField(max_length=255)

    get_started_step_3_heading = models.CharField(max_length=255)
    get_started_step_3_description = RichTextField()
    get_started_step_3_cta = models.CharField(max_length=255)

    adopt_heading = models.CharField(max_length=255)
    adopt_description = RichTextField()
    adopt_cta = models.CharField(max_length=255)

    row_2 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])
    row_3 = StreamField([
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
        ]))
    ])

    api_fields = (
        'intro_heading',
        'intro_description',
        'row_1',
        'get_started_heading',
        'get_started_step_1_heading',
        'get_started_step_1_description',
        'get_started_step_1_cta',
        'get_started_step_2_heading',
        'get_started_step_2_description',
        'get_started_step_2_cta',
        'get_started_step_3_heading',
        'get_started_step_3_description',
        'get_started_step_3_cta',
        'adopt_heading',
        'adopt_description',
        'adopt_cta',
        'row_2',
        'row_3',
        'slug',
        'seo_title',
        'search_description',)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        StreamFieldPanel('row_1'),
        FieldPanel('get_started_heading'),
        FieldPanel('get_started_step_1_heading'),
        FieldPanel('get_started_step_1_description'),
        FieldPanel('get_started_step_1_cta'),
        FieldPanel('get_started_step_2_heading'),
        FieldPanel('get_started_step_2_description'),
        FieldPanel('get_started_step_2_cta'),
        FieldPanel('get_started_step_3_heading'),
        FieldPanel('get_started_step_3_description'),
        FieldPanel('get_started_step_3_cta'),
        FieldPanel('adopt_heading'),
        FieldPanel('adopt_description'),
        FieldPanel('adopt_cta'),
        StreamFieldPanel('row_2'),
        StreamFieldPanel('row_3'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class ContactUs(Page):
    tagline = models.CharField(max_length=255)
    mailing_header = models.CharField(max_length=255)
    mailing_address = RichTextField()
    phone_number = models.CharField(max_length=255)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tagline'),
        FieldPanel('mailing_header'),
        FieldPanel('mailing_address'),
        FieldPanel('phone_number'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    api_fields = (
        'title',
        'tagline',
        'mailing_header',
        'mailing_address',
        'phone_number',
        'slug',
        'seo_title',
        'search_description',
    )

    parent_page_types = ['pages.HomePage']


class GeneralPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('tagline', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('multicolumn', blocks.StreamBlock([
            ('column', ColumnBlock()),
            ],
            icon='placeholder'
        )),
        ('person', PersonBlock()),
        ('html', RawHTMLBlock()),
    ])

    api_fields = (
        'title',
        'body',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title'),
        StreamFieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    def serve(self, request, *args, **kwargs):
        data = {
            'title': self.title,
            'slug': self.slug,
            'seo_title': self.seo_title,
            'search_description': self.search_description,
            'body': self.body,
        }

        return JsonResponse(data)


class EcosystemAllies(Page):
    classroom_text = RichTextField()

    api_fields = (
        'title',
        'classroom_text',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('classroom_text'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']
