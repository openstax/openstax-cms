from django import forms
from django.db import models
from django.http.response import JsonResponse
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                StreamFieldPanel)
from wagtail.core import blocks
from wagtail.core.blocks import FieldBlock, RawHTMLBlock, StructBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from openstax.functions import build_image_url, build_document_url
from wagtail.api import APIField

from books.models import Book
from api.serializers import ImageSerializer

from salesforce.models import PartnerTypeMapping, PartnerFieldNameMapping, PartnerCategoryMapping, Partner


### Custom Block Definitions ###

class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),))


class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    alt_text = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    alignment = ImageFormatChoiceBlock()
    identifier = blocks.CharBlock(required=False, help_text="Used by the frontend for Google Analytics.")


class APIImageChooserBlock(ImageChooserBlock): # Use this block to return the path in the page API, does not support alt_text and alignment
    def get_api_representation(self, value, context=None):
        try:
            return ImageSerializer(context=context).to_representation(value)
        except AttributeError:
            return None

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
        icon = 'placeholder'


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


### Secondary Model Definitions ###

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


class Funder(models.Model):
    title = models.CharField(max_length=250)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_funder_logo(self):
        return build_image_url(self.logo)
    funder_logo = property(get_funder_logo)
    description = models.TextField(blank=True, null=True)

    api_fields = ('title', 'funder_logo', 'description', )

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('logo'),
        FieldPanel('description'),
    ]


class Institutions(models.Model):
    title = models.CharField(max_length=250)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image should be 340px wide, horizontal images are ideal'
    )

    def get_institution_logo(self):
        return build_image_url(self.logo)
    institution_logo = property(get_institution_logo)

    api_fields = ('title', 'institution_logo')

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('logo'),
    ]


class MarketingVideoLink(models.Model):
    video_title = models.CharField(max_length=255, blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='marketing_videos', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    video_image_blurb = models.CharField(max_length=255, null=True, blank=True)

    def get_image(self):
        return build_image_url(self.image_file)
    image = property(get_image)

    api_fields = ('video_title',
                  'video_url',
                  'video_file',
                  'image_url',
                  'image',
                  'video_image_blurb',)

    panels = [
        FieldPanel('video_title'),
        FieldPanel('video_url'),
        FieldPanel('video_file'),
        FieldPanel('image_url'),
        ImageChooserPanel('image_file'),
        FieldPanel('video_image_blurb'),
    ]

class Resource(models.Model):
    name = models.CharField(max_length=255, help_text="Resources should be added in pairs to display properly.")
    available = models.BooleanField(default=False)
    available_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    def get_available_image(self):
        return build_image_url(self.available_image)
    available_image_url = property(get_available_image)

    alternate_text = models.CharField(max_length=255, null=True, blank=True, help_text="If this has text, availability is ignored.")

    api_fields = ('name',
                  'available',
                  'available_image_url',
                  'alternate_text')

    panels = [
        FieldPanel('name'),
        FieldPanel('available'),
        ImageChooserPanel('available_image'),
        FieldPanel('alternate_text'),
    ]

class Group(models.Model):
    heading = models.CharField(max_length=255)
    people = StreamField([
        ('person', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock(required=False)),
            ('bio', blocks.CharBlock(required=False)),
            ('photo', APIImageChooserBlock(required=False)),
        ], icon='user')),
    ])

    api_fields = ('heading',
                  'people', )

    panels = [
        FieldPanel('heading'),
        StreamFieldPanel('people'),
    ]

class Card(models.Model):
    heading = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cards = StreamField([
        ('card', blocks.StructBlock([
            ('image', ImageBlock()),
            ('headline', blocks.TextBlock(required=False)),
            ('description', blocks.TextBlock(required=False)),
            ('button_text', blocks.CharBlock(required=False)),
            ('button_url', blocks.CharBlock(required=False))
        ], icon='document')),
    ])

    api_fields = ('heading',
                  'description',
                  'cards')

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        StreamFieldPanel('cards')
    ]

### Orderable Through-Models ###

class OpenStaxPeople(Orderable, Group):
    marketing_video = ParentalKey(
        'pages.TeamPage', related_name='openstax_people')

class FoundationSupportFunders(Orderable, Funder):
    page = ParentalKey('pages.FoundationSupport', related_name='funders')


class OurImpactInstitutions(Orderable, Institutions):
    page = ParentalKey('pages.OurImpact', related_name='institutions')

class MarketingVideos(Orderable, MarketingVideoLink):
    marketing_video = ParentalKey(
        'pages.Marketing', related_name='marketing_videos')


class ResourceAvailability(Orderable, Resource):
    marketing_video = ParentalKey(
        'pages.Marketing', related_name='resource_availability')

### Page Definitions ###

class AboutUsPage(Page):
    who_heading = models.CharField(max_length=255)
    who_paragraph = models.TextField()
    who_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_who_image(self):
        return build_image_url(self.who_image)
    who_image_url = property(get_who_image)
    what_heading = models.CharField(max_length=255)
    what_paragraph = models.TextField()
    what_cards = StreamField([
        ('card', blocks.StreamBlock([
            ('image', ImageBlock()),
            ('paragraph', blocks.TextBlock())
        ],
            icon='placeholder'
        )),
    ])
    where_heading = models.CharField(max_length=255)
    where_paragraph = models.TextField()
    where_map = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_where_map(self):
        return build_image_url(self.where_map)
    where_map_alt = models.CharField(max_length=255, blank=True, null=True)
    where_map_url = property(get_where_map)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('who_heading'),
        APIField('who_paragraph'),
        APIField('who_image'),
        APIField('who_image_url'),
        APIField('what_heading'),
        APIField('what_paragraph'),
        APIField('what_cards'),
        APIField('where_heading'),
        APIField('where_paragraph'),
        APIField('where_map'),
        APIField('where_map_alt'),
        APIField('where_map_url'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('who_heading'),
        FieldPanel('who_paragraph'),
        ImageChooserPanel('who_image'),
        FieldPanel('what_heading'),
        FieldPanel('what_paragraph'),
        StreamFieldPanel('what_cards'),
        FieldPanel('where_heading'),
        FieldPanel('where_paragraph'),
        ImageChooserPanel('where_map'),
        FieldPanel('where_map_alt'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class TeamPage(Page):
    header = models.TextField(max_length=255)
    subheader = models.TextField(max_length=255)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_header_image(self):
        return build_image_url(self.header_image)
    header_image_url = property(get_header_image)

    team_header = models.CharField(max_length=255, null=True, blank=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('header'),
        FieldPanel('subheader'),
        ImageChooserPanel('header_image'),
        FieldPanel('team_header'),
        InlinePanel('openstax_people', label="OpenStax People"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    api_fields = [
        APIField('title'),
        APIField('header'),
        APIField('subheader'),
        APIField('header_image_url'),
        APIField('team_header'),
        APIField('openstax_people'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    template = 'page.html'
    max_count = 1


class HomePage(Page):
    banner_images = StreamField([
        ('image', ImageBlock())
    ], null=True)
    mobile_banner_images = StreamField([
        ('image', ImageBlock())
    ], null=True, blank=True)
    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])
    row_2 = StreamField([
        ('column', ColumnBlock()),
    ])
    row_3 = StreamField([
        ('column', ColumnBlock()),
    ])
    row_4 = StreamField([
        ('column', ColumnBlock()),
    ])
    row_5 = StreamField([
        ('column', ColumnBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('mobile_banner_images'),
        APIField('banner_images'),
        APIField('row_1'),
        APIField('row_2'),
        APIField('row_3'),
        APIField('row_4'),
        APIField('row_5'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    max_count = 1

    class Meta:
        verbose_name = "Home Page"


    content_panels = [
        FieldPanel('title', classname="full title"),
        StreamFieldPanel('mobile_banner_images'),
        StreamFieldPanel('banner_images'),
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
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    # we are controlling what types of pages are allowed under a homepage
    # if a new page type is created, it needs to be added here to show up in
    # the admin
    subpage_types = [
        'pages.HigherEducation',
        'pages.ContactUs',
        'pages.AboutUsPage',
        'pages.TeamPage',
        'pages.GeneralPage',
        'pages.FoundationSupport',
        'pages.OurImpact',
        'pages.MapPage',
        'pages.Give',
        'pages.TermsOfService',
        'pages.AP',
        'pages.FAQ',
        'pages.Support',
        'pages.GiveForm',
        'pages.Accessibility',
        'pages.Licensing',
        'pages.CompCopy',
        'pages.AdoptForm',
        'pages.InterestForm',
        'pages.Marketing',
        'pages.Technology',
        'pages.ErrataList',
        'pages.PrivacyPolicy',
        'pages.PrintOrder',
        'pages.ResearchPage',
        'pages.Careers',
        'pages.RoverPage',
        'pages.AnnualReportPage',
        'pages.InstitutionalPartnership',
        'pages.HeroJourneyPage',
        'pages.InstitutionalPartnerProgramPage',
        'pages.CreatorFestPage',
        'pages.PartnersPage',
        'pages.WebinarPage',
        'pages.MathQuizPage',
        'books.BookIndex',
        'news.NewsIndex',
        'news.PressIndex'
    ]

    max_count = 1

    def __str__(self):
        return self.path

    def get_url_parts(self, *args, **kwargs):
        url_parts = super(HomePage, self).get_url_parts(*args, **kwargs)

        if url_parts is None:
            # in this case, the page doesn't have a well-defined URL in the first place -
            # for example, it's been created at the top level of the page tree
            # and hasn't been associated with a site record
            return None

        site_id, root_url, page_path = url_parts

        # return '/' in place of the real page path
        return (site_id, root_url, '/')

    class Meta:
        verbose_name = "homepage"


class HigherEducation(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()

    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])

    get_started_heading = models.CharField(max_length=255)

    get_started_step_1_heading = models.CharField(max_length=255)
    get_started_step_1_description = models.TextField()
    get_started_step_1_cta = models.CharField(max_length=255)

    get_started_step_2_heading = models.CharField(max_length=255)
    get_started_step_2_description = models.TextField()
    get_started_step_2_logged_in_cta = models.CharField(max_length=255)
    get_started_step_2_logged_out_cta = models.CharField(max_length=255)

    get_started_step_3_heading = models.CharField(max_length=255)
    get_started_step_3_description = models.TextField()
    get_started_step_3_cta = models.CharField(max_length=255)

    adopt_heading = models.CharField(max_length=255)
    adopt_description = models.TextField()
    adopt_cta = models.CharField(max_length=255)

    row_2 = StreamField([
        ('column', ColumnBlock()),
    ])
    row_3 = StreamField([
        ('column', ColumnBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('row_1'),
        APIField('get_started_heading'),
        APIField('get_started_step_1_heading'),
        APIField('get_started_step_1_description'),
        APIField('get_started_step_1_cta'),
        APIField('get_started_step_2_heading'),
        APIField('get_started_step_2_description'),
        APIField('get_started_step_2_logged_in_cta'),
        APIField('get_started_step_2_logged_out_cta'),
        APIField('get_started_step_3_heading'),
        APIField('get_started_step_3_description'),
        APIField('get_started_step_3_cta'),
        APIField('adopt_heading'),
        APIField('adopt_description'),
        APIField('adopt_cta'),
        APIField('row_2'),
        APIField('row_3'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

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
        FieldPanel('get_started_step_2_logged_in_cta'),
        FieldPanel('get_started_step_2_logged_out_cta'),
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
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class ContactUs(Page):
    tagline = models.CharField(max_length=255)
    mailing_header = models.CharField(max_length=255)
    mailing_address = RichTextField()
    customer_service = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tagline'),
        FieldPanel('mailing_header'),
        FieldPanel('mailing_address'),
        FieldPanel('customer_service'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    api_fields = [
        APIField('title'),
        APIField('tagline'),
        APIField('mailing_header'),
        APIField('mailing_address'),
        APIField('customer_service'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class GeneralPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('tagline', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', APIImageChooserBlock()),
        ('html', RawHTMLBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('body'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title'),
        StreamFieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]


class FoundationSupport(Page):
    page_description = models.TextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('page_description'),
        APIField('funders'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('page_description'),
        InlinePanel('funders', label="Funders"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class OurImpact(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()

    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('row_1'),
        APIField('institutions'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        StreamFieldPanel('row_1'),
        InlinePanel('institutions', label="Institutions"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class MapPage(Page):
    header_text = models.CharField(max_length=255)
    map_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_map_image(self):
        return build_image_url(self.map_image)
    map_image_url = property(get_map_image)
    section_1_cards = StreamField([
        ('card', blocks.StructBlock([
            ('image', ImageBlock()),
            ('number', blocks.CharBlock(required=False)),
            ('unit', blocks.CharBlock(required=False)),
            ('description', blocks.TextBlock(required=False)),
        ], icon='document')),
    ], null=True)
    section_2_header_1 = models.CharField(max_length=255)
    section_2_blurb_1 = models.TextField()
    section_2_cta_1 = models.CharField(max_length=255)
    section_2_link_1 = models.CharField(max_length=255)
    section_2_image_1 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_section_2_image_1(self):
        return build_image_url(self.section_2_image_1)
    section_2_image_1_url = property(get_section_2_image_1)
    section_2_header_2 = models.CharField(max_length=255)
    section_2_blurb_2 = models.TextField()
    section_2_cta_2 = models.CharField(max_length=255)
    section_2_link_2 = models.CharField(max_length=255)
    section_2_image_2 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_section_2_image_2(self):
        return build_image_url(self.section_2_image_2)
    section_2_image_2_url = property(get_section_2_image_2)
    section_3_heading = models.CharField(max_length=255)
    section_3_blurb = models.TextField()
    section_3_cta = models.CharField(max_length=255)
    section_3_link = models.CharField(max_length=255)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('header_text'),
        APIField('section_1_cards'),
        APIField('map_image_url'),
        APIField('section_2_header_1'),
        APIField('section_2_blurb_1'),
        APIField('section_2_cta_1'),
        APIField('section_2_link_1'),
        APIField('section_2_image_1_url'),
        APIField('section_2_header_2'),
        APIField('section_2_blurb_2'),
        APIField('section_2_cta_2'),
        APIField('section_2_link_2'),
        APIField('section_2_image_2_url'),
        APIField('section_3_heading'),
        APIField('section_3_blurb'),
        APIField('section_3_cta'),
        APIField('section_3_link'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('header_text'),
        ImageChooserPanel('map_image'),
        StreamFieldPanel('section_1_cards'),
        FieldPanel('section_2_header_1'),
        FieldPanel('section_2_blurb_1'),
        FieldPanel('section_2_cta_1'),
        FieldPanel('section_2_link_1'),
        ImageChooserPanel('section_2_image_1'),
        FieldPanel('section_2_header_2'),
        FieldPanel('section_2_blurb_2'),
        FieldPanel('section_2_cta_2'),
        FieldPanel('section_2_link_2'),
        ImageChooserPanel('section_2_image_2'),
        FieldPanel('section_3_heading'),
        FieldPanel('section_3_blurb'),
        FieldPanel('section_3_cta'),
        FieldPanel('section_3_link'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Give(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()
    other_payment_methods_heading = models.CharField(max_length=255)
    payment_method_1_heading = models.CharField(max_length=255)
    payment_method_1_content = RichTextField()
    payment_method_2_heading = models.CharField(max_length=255)
    payment_method_2_content = RichTextField()
    payment_method_3_heading = models.CharField(max_length=255)
    payment_method_3_content = RichTextField()
    payment_method_4_heading = models.CharField(max_length=255, blank=True, null=True)
    payment_method_4_content = RichTextField(blank=True, null=True)
    give_cta = models.CharField(max_length=255)
    give_cta_link = models.URLField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('other_payment_methods_heading'),
        APIField('payment_method_1_heading'),
        APIField('payment_method_1_content'),
        APIField('payment_method_2_heading'),
        APIField('payment_method_2_content'),
        APIField('payment_method_3_heading'),
        APIField('payment_method_3_content'),
        APIField('payment_method_4_heading'),
        APIField('payment_method_4_content'),
        APIField('give_cta'),
        APIField('give_cta_link'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('other_payment_methods_heading'),
        FieldPanel('payment_method_1_heading'),
        FieldPanel('payment_method_1_content'),
        FieldPanel('payment_method_2_heading'),
        FieldPanel('payment_method_2_content'),
        FieldPanel('payment_method_3_heading'),
        FieldPanel('payment_method_3_content'),
        FieldPanel('payment_method_4_heading'),
        FieldPanel('payment_method_4_content'),
        FieldPanel('give_cta'),
        FieldPanel('give_cta_link'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class TermsOfService(Page):
    intro_heading = models.CharField(max_length=255)
    terms_of_service_content = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('terms_of_service_content'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('terms_of_service_content'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class AP(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()

    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])

    row_2 = StreamField([
        ('column', ColumnBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('row_1'),
        APIField('row_2'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        StreamFieldPanel('row_1'),
        StreamFieldPanel('row_2'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class FAQ(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    questions = StreamField([
        ('question', FAQBlock()),
    ])

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('questions'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        StreamFieldPanel('questions'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Support(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()

    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('row_1'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        StreamFieldPanel('row_1'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class GiveForm(Page):
    page_description = models.TextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('page_description'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('page_description'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Accessibility(Page):
    intro_heading = models.CharField(max_length=255)
    accessibility_content = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('accessibility_content'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('accessibility_content'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Licensing(Page):
    intro_heading = models.CharField(max_length=255)
    licensing_content = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('licensing_content'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('licensing_content'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class CompCopy(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class AdoptForm(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')

    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class InterestForm(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Marketing(Page):
    #hover box text
    pop_up_text = RichTextField()
    #access tutor section
    access_tagline = models.CharField(max_length=255)
    access_button_cta = models.CharField(max_length=255)
    access_button_link = models.URLField()
    #section 1 - discover header
    section_1_heading = models.CharField(max_length=255)
    section_1_subheading = models.CharField(max_length=255)
    section_1_paragraph = RichTextField()
    section_1_cta_link = models.URLField()
    section_1_cta_text = models.CharField(max_length=255)
    #section 2 - how does it work?
    section_2_heading = models.CharField(max_length=255)
    section_2_subheading = models.CharField(max_length=255)
    section_2_paragraph = RichTextField()
    icon_1_image = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_icon_1_image(self):
        return build_document_url(self.icon_1_image.url)
    icon_1_image_url = property(get_icon_1_image)

    icon_1_subheading = models.CharField(max_length=255)
    icon_1_paragraph = models.CharField(max_length=255)
    icon_2_image = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_icon_2_image(self):
        return build_document_url(self.icon_2_image.url)
    icon_2_image_url = property(get_icon_2_image)


    icon_2_subheading = models.CharField(max_length=255)
    icon_2_paragraph = models.CharField(max_length=255)
    icon_3_image = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_icon_3_image(self):
        return build_document_url(self.icon_3_image.url)
    icon_3_image_url = property(get_icon_3_image)

    icon_3_subheading = models.CharField(max_length=255)
    icon_3_paragraph = models.CharField(max_length=255)
    icon_4_image = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_icon_4_image(self):
        return build_document_url(self.icon_4_image.url)
    icon_4_image_url = property(get_icon_4_image)

    icon_4_subheading = models.CharField(max_length=255)
    icon_4_paragraph = models.CharField(max_length=255)
    #section 3 - what your students will see
    section_3_heading = models.CharField(max_length=255)
    section_3_paragraph = RichTextField()
    #marketing videos orderable resource
    #section 4 - current features and plans
    #resource availability via orderable resource
    section_4_heading = models.CharField(max_length=255)
    section_4_paragraph = RichTextField()
    section_4_resource_fine_print = models.CharField(max_length=255)
    section_4_book_heading = models.CharField(max_length=255)
    section_4_coming_soon_heading = models.CharField(max_length=255)
    section_4_coming_soon_text = RichTextField()
    #section 5 - $10
    section_5_heading = models.CharField(max_length=255)
    section_5_paragraph = RichTextField()
    #science
    section_5_science_heading = models.CharField(max_length=255)
    section_5_science_paragraph = RichTextField()
    #section 6 - FAQs
    section_6_heading = models.CharField(max_length=255)
    section_6_knowledge_base_copy = RichTextField()
    faqs = StreamField([
        ('faq', FAQBlock()),
    ])
    #section 7 - a new way of teaching
    section_7_heading = models.CharField(max_length=255)
    section_7_subheading = models.CharField(max_length=255)
    section_7_cta_text_1 = models.CharField(max_length=255)
    section_7_cta_link_1 = models.URLField()
    section_7_cta_blurb_1 = models.CharField(max_length=255)
    section_7_cta_text_2 = models.CharField(max_length=255, blank=True, null=True)
    section_7_cta_link_2 = models.URLField(blank=True, null=True)
    section_7_cta_blurb_2 = models.CharField(max_length=255, blank=True, null=True)
    #floating footer
    floating_footer_button_1_cta = models.CharField(max_length=255)
    floating_footer_button_1_link = models.URLField()
    floating_footer_button_1_caption = models.CharField(max_length=255)
    floating_footer_button_2_cta = models.CharField(max_length=255)
    floating_footer_button_2_link = models.URLField()
    floating_footer_button_2_caption = models.CharField(max_length=255)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def marketing_books(self):
        books = Book.objects.filter(tutor_marketing_book=True).order_by('path')
        book_data = []
        for book in books:
            book_data.append({
                'id': book.id,
                'slug': 'books/{}'.format(book.slug),
                'title': book.title,
                'cover_url': book.cover_url,
            })
        return book_data

    api_fields = [
        APIField('title'),
        APIField('pop_up_text'),
        APIField('access_tagline'),
        APIField('access_button_cta'),
        APIField('access_button_link'),
        APIField('section_1_heading'),
        APIField('section_1_subheading'),
        APIField('section_1_paragraph'),
        APIField('section_1_cta_link'),
        APIField('section_1_cta_text'),
        APIField('section_2_heading'),
        APIField('section_2_subheading'),
        APIField('section_2_paragraph'),
        APIField('icon_1_image_url'),
        APIField('icon_1_subheading'),
        APIField('icon_1_paragraph'),
        APIField('icon_2_image_url'),
        APIField('icon_2_subheading'),
        APIField('icon_2_paragraph'),
        APIField('icon_3_image_url'),
        APIField('icon_3_subheading'),
        APIField('icon_3_paragraph'),
        APIField('icon_4_image_url'),
        APIField('icon_4_subheading'),
        APIField('icon_4_paragraph'),
        APIField('section_3_heading'),
        APIField('section_3_paragraph'),
        APIField('marketing_videos'),
        APIField('resource_availability'),
        APIField('section_4_heading'),
        APIField('section_4_paragraph'),
        APIField('section_4_resource_fine_print'),
        APIField('marketing_books'),
        APIField('section_4_book_heading'),
        APIField('section_4_coming_soon_heading'),
        APIField('section_4_coming_soon_text'),
        APIField('section_5_heading'),
        APIField('section_5_paragraph'),
        APIField('section_5_science_heading'),
        APIField('section_5_science_paragraph'),
        APIField('section_6_heading'),
        APIField('section_6_knowledge_base_copy'),
        APIField('faqs'),
        APIField('section_7_heading'),
        APIField('section_7_subheading'),
        APIField('section_7_cta_text_1'),
        APIField('section_7_cta_link_1'),
        APIField('section_7_cta_blurb_1'),
        APIField('section_7_cta_text_2'),
        APIField('section_7_cta_link_2'),
        APIField('section_7_cta_blurb_2'),
        APIField('floating_footer_button_1_cta'),
        APIField('floating_footer_button_1_link'),
        APIField('floating_footer_button_1_caption'),
        APIField('floating_footer_button_2_cta'),
        APIField('floating_footer_button_2_link'),
        APIField('floating_footer_button_2_caption'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('pop_up_text'),
        FieldPanel('access_tagline'),
        FieldPanel('access_button_cta'),
        FieldPanel('access_button_link'),
        FieldPanel('section_1_heading'),
        FieldPanel('section_1_heading'),
        FieldPanel('section_1_heading'),
        FieldPanel('section_1_subheading'),
        FieldPanel('section_1_paragraph'),
        FieldPanel('section_1_cta_link'),
        FieldPanel('section_1_cta_text'),
        FieldPanel('section_2_heading'),
        FieldPanel('section_2_subheading'),
        FieldPanel('section_2_paragraph'),
        DocumentChooserPanel('icon_1_image'),
        FieldPanel('icon_1_subheading'),
        FieldPanel('icon_1_paragraph'),
        DocumentChooserPanel('icon_2_image'),
        FieldPanel('icon_2_subheading'),
        FieldPanel('icon_2_paragraph'),
        DocumentChooserPanel('icon_3_image'),
        FieldPanel('icon_3_subheading'),
        FieldPanel('icon_3_paragraph'),
        DocumentChooserPanel('icon_4_image'),
        FieldPanel('icon_4_subheading'),
        FieldPanel('icon_4_paragraph'),
        FieldPanel('section_3_heading'),
        FieldPanel('section_3_paragraph'),
        InlinePanel('marketing_videos', label="Marketing Videos"),
        FieldPanel('section_4_heading'),
        FieldPanel('section_4_paragraph'),
        InlinePanel('resource_availability', label="Resource Availability"),
        FieldPanel('section_4_resource_fine_print'),
        FieldPanel('section_4_book_heading'),
        FieldPanel('section_4_coming_soon_heading'),
        FieldPanel('section_4_coming_soon_text'),
        FieldPanel('section_5_heading'),
        FieldPanel('section_5_paragraph'),
        FieldPanel('section_5_science_heading'),
        FieldPanel('section_5_science_paragraph'),
        FieldPanel('section_6_heading'),
        FieldPanel('section_6_knowledge_base_copy'),
        StreamFieldPanel('faqs'),
        FieldPanel('section_7_heading'),
        FieldPanel('section_7_subheading'),
        FieldPanel('section_7_cta_text_1'),
        FieldPanel('section_7_cta_link_1'),
        FieldPanel('section_7_cta_blurb_1'),
        FieldPanel('section_7_cta_text_2'),
        FieldPanel('section_7_cta_link_2'),
        FieldPanel('section_7_cta_blurb_2'),
        FieldPanel('floating_footer_button_1_cta'),
        FieldPanel('floating_footer_button_1_link'),
        FieldPanel('floating_footer_button_1_caption'),
        FieldPanel('floating_footer_button_2_cta'),
        FieldPanel('floating_footer_button_2_link'),
        FieldPanel('floating_footer_button_2_caption'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Technology(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()

    banner_cta = models.CharField(max_length=255)
    banner_cta_link = models.URLField(blank=True, null=True)

    select_tech_heading = models.CharField(max_length=255)
    select_tech_step_1 = models.CharField(max_length=255)
    select_tech_step_2 = models.CharField(max_length=255)
    select_tech_step_3 = models.CharField(max_length=255)

    new_frontier_heading = models.CharField(max_length=255)
    new_frontier_subheading = models.CharField(max_length=255)
    new_frontier_description = RichTextField()
    new_frontier_cta_1 = models.CharField(max_length=255)
    new_frontier_cta_link_1 = models.URLField(blank=True, null=True)
    new_frontier_cta_2 = models.CharField(max_length=255)
    new_frontier_cta_link_2 = models.URLField(blank=True, null=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('banner_cta'),
        APIField('banner_cta_link'),
        APIField('select_tech_heading'),
        APIField('select_tech_step_1'),
        APIField('select_tech_step_2'),
        APIField('select_tech_step_3'),
        APIField('new_frontier_heading'),
        APIField('new_frontier_subheading'),
        APIField('new_frontier_description'),
        APIField('new_frontier_cta_1'),
        APIField('new_frontier_cta_link_1'),
        APIField('new_frontier_cta_2'),
        APIField('new_frontier_cta_link_2'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('banner_cta'),
        FieldPanel('banner_cta_link'),
        FieldPanel('select_tech_heading'),
        FieldPanel('select_tech_step_1'),
        FieldPanel('select_tech_step_2'),
        FieldPanel('select_tech_step_3'),
        FieldPanel('new_frontier_heading'),
        FieldPanel('new_frontier_subheading'),
        FieldPanel('new_frontier_description'),
        FieldPanel('new_frontier_cta_1'),
        FieldPanel('new_frontier_cta_link_1'),
        FieldPanel('new_frontier_cta_2'),
        FieldPanel('new_frontier_cta_link_2'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class ErrataList(Page):
    correction_schedule = RichTextField()
    deprecated_errata_message = RichTextField(help_text="Errata message for deprecated books, controlled via the book state field.")
    new_edition_errata_message = RichTextField(help_text="Errata message for books with new editions, controlled via the book state field.")

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('correction_schedule'),
        APIField('deprecated_errata_message'),
        APIField('new_edition_errata_message'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('correction_schedule'),
        FieldPanel('deprecated_errata_message'),
        FieldPanel('new_edition_errata_message')
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class PrivacyPolicy(Page):
    intro_heading = models.CharField(max_length=255)
    privacy_content = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('privacy_content'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('privacy_content'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class PrintOrder(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()
    featured_provider_intro_blurb = models.TextField()
    featured_providers = StreamField([
        ('provider', BookProviderBlock(icon='document')),
    ], null=True)
    other_providers_intro_blurb = models.TextField()
    providers = StreamField([
        ('provider', BookProviderBlock(icon='document')),
    ])
    us_isbn_download = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_us_isbn_download(self):
        return build_document_url(self.us_isbn_download.url)

    us_isbn_download_url = property(get_us_isbn_download)
    us_isbn_cta = models.CharField(max_length=255)

    canadian_isbn_download = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_canadian_isbn_download(self):
        return build_document_url(self.canadian_isbn_download.url)

    canadian_isbn_download_url = property(get_canadian_isbn_download)
    canadian_isbn_cta = models.CharField(max_length=255)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('intro_description'),
        APIField('featured_provider_intro_blurb'),
        APIField('featured_providers'),
        APIField('other_providers_intro_blurb'),
        APIField('providers'),
        APIField('us_isbn_download_url'),
        APIField('us_isbn_cta'),
        APIField('canadian_isbn_download_url'),
        APIField('canadian_isbn_cta'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('featured_provider_intro_blurb'),
        StreamFieldPanel('featured_providers'),
        FieldPanel('other_providers_intro_blurb'),
        StreamFieldPanel('providers'),
        DocumentChooserPanel('us_isbn_download'),
        FieldPanel('us_isbn_cta'),
        DocumentChooserPanel('canadian_isbn_download'),
        FieldPanel('canadian_isbn_cta'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class ResearchPage(Page):
    mission_header = models.CharField(max_length=255)
    mission_body = models.TextField()
    projects_header = models.CharField(max_length=255)
    projects = StreamField([
        ('project', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('blurb', blocks.TextBlock()),
            ('link', blocks.URLBlock(required=False, help_text="Optional link to project."))
        ], icon='user')),
    ], null=True, blank=True)
    people_header = models.CharField(max_length=255)
    alumni = StreamField([
        ('person', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('website', blocks.URLBlock(required=False)),
        ], icon='user')),
    ], null=True, blank=True)
    current_members = StreamField([
        ('person', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('photo', APIImageChooserBlock(required=False)),
            ('website', blocks.URLBlock(required=False)),
        ], icon='user')),
    ], null=True, blank=True)
    external_collaborators = StreamField([
        ('person', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('photo', APIImageChooserBlock(required=False)),
            ('website', blocks.URLBlock(required=False)),
        ], icon='user')),
    ], null=True, blank=True)
    publication_header = models.CharField(max_length=255)
    publications = StreamField([
        ('publication', blocks.StructBlock([
            ('authors', blocks.CharBlock()),
            ('date', blocks.DateBlock()),
            ('title', blocks.CharBlock()),
            ('excerpt', blocks.CharBlock()),
            ('download_url', blocks.URLBlock()),
        ], icon='user')),
    ], null=True, blank=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('mission_header'),
        FieldPanel('mission_body'),
        FieldPanel('projects_header'),
        StreamFieldPanel('projects'),
        FieldPanel('people_header'),
        StreamFieldPanel('alumni'),
        StreamFieldPanel('current_members'),
        StreamFieldPanel('external_collaborators'),
        FieldPanel('publication_header'),
        StreamFieldPanel('publications'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    api_fields = [
        APIField('mission_header'),
        APIField('mission_body'),
        APIField('projects_header'),
        APIField('projects'),
        APIField('people_header'),
        APIField('alumni'),
        APIField('current_members'),
        APIField('external_collaborators'),
        APIField('publication_header'),
        APIField('publications'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Careers(Page):
    intro_heading = models.CharField(max_length=255)
    careers_content = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('intro_heading'),
        APIField('careers_content'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('careers_content'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    max_count = 1


class RoverPage(Page):
        nav_title = models.CharField(max_length=255, null=True, blank=True)
        section_1 = StreamField([
            ('access_button_link', blocks.URLBlock()),
            ('access_button_cta', blocks.CharBlock()),
            ('image', APIImageChooserBlock()),
            ('blurb', blocks.TextBlock()),
            ('button_link', blocks.URLBlock()),
            ('button_cta', blocks.CharBlock()),
            ('nav_text', blocks.CharBlock(required=False))
        ])
        section_2 = StreamField([
            ('video', blocks.RawHTMLBlock()),
            ('heading', blocks.CharBlock()),
            ('subheading', blocks.TextBlock()),
            ('blurb', blocks.TextBlock()),
            ('nav_text', blocks.CharBlock(required=False))
        ])
        section_3 = StreamField([
            ('heading', blocks.CharBlock()),
            ('subheading', blocks.TextBlock()),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('icon', APIImageChooserBlock()),
                ('blurb', blocks.TextBlock())
            ]))),
            ('button_link', blocks.URLBlock()),
            ('button_cta', blocks.CharBlock()),
            ('nav_text', blocks.CharBlock(required=False))
        ])
        section_4 = StreamField([
            ('heading', blocks.CharBlock()),
            ('blurb', blocks.TextBlock()),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('blurb', blocks.TextBlock()),
                ('image', APIImageChooserBlock()),
                ('image_alt_text', blocks.CharBlock())
            ]))),
            ('nav_text', blocks.CharBlock(required=False))
        ])
        section_5 = StreamField([
            ('heading', blocks.CharBlock()),
            ('blurb', blocks.TextBlock()),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('video', blocks.RawHTMLBlock()),
                ('heading', blocks.CharBlock()),
                ('blurb', blocks.TextBlock())
            ]))),
            ('nav_text', blocks.CharBlock(required=False)),
            ('see_more_text', blocks.CharBlock(required=False)),
            ('see_more_url', blocks.URLBlock(required=False))
        ], null=True, blank=True)
        section_6 = StreamField([
            ('heading', blocks.CharBlock()),
            ('blurb', blocks.RichTextBlock()),
            ('image', APIImageChooserBlock()),
            ('image_alt_text', blocks.CharBlock()),
            ('caption', blocks.CharBlock()),
            ('nav_text', blocks.CharBlock(required=False))
        ])
        section_7 = StreamField([
            ('faqs', blocks.ListBlock(blocks.StructBlock([
                ('question', blocks.CharBlock()),
                ('answer', blocks.TextBlock())
            ]))),
            ('webinar_button_url', blocks.URLBlock()),
            ('webinar_button_cta', blocks.CharBlock()),
            ('signup_button_url', blocks.URLBlock()),
            ('signup_button_cta', blocks.CharBlock()),
            ('nav_text', blocks.CharBlock(required=False))
        ])
        popup = StreamField([
            ('content', blocks.ListBlock(blocks.StructBlock([
                ('headline', blocks.CharBlock()),
                ('instructions', blocks.TextBlock()),
                ('sign_in_text', blocks.CharBlock()),
                ('other_option_text', blocks.CharBlock()),
                ('other_option_url', blocks.URLBlock()),
                ('background_image', APIImageChooserBlock())
            ])))
        ], null=True)
        office_hours = StreamField([
            ('content', blocks.ListBlock(blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('description', blocks.RichTextBlock()),
                ('more_info', blocks.RichTextBlock()),
                ('image', APIImageChooserBlock()),
                ('link_url', blocks.URLBlock()),
                ('link_text', blocks.CharBlock())
            ])))
        ], null=True, blank=True)
        promote_image = models.ForeignKey(
            'wagtailimages.Image',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='+'
        )

        content_panels = [
            FieldPanel('title', classname='full title', help_text="Internal name for page."),
            FieldPanel('nav_title', help_text="Sets navigation menu title."),
            StreamFieldPanel('section_1'),
            StreamFieldPanel('section_2'),
            StreamFieldPanel('section_3'),
            StreamFieldPanel('section_4'),
            StreamFieldPanel('section_5'),
            StreamFieldPanel('section_6'),
            StreamFieldPanel('section_7'),
            StreamFieldPanel('popup'),
            StreamFieldPanel('office_hours'),
        ]

        promote_panels = [
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            ImageChooserPanel('promote_image')

        ]

        api_fields = [
            APIField('title'),
            APIField('nav_title'),
            APIField('section_1'),
            APIField('section_2'),
            APIField('section_3'),
            APIField('section_4'),
            APIField('section_5'),
            APIField('section_6'),
            APIField('section_7'),
            APIField('popup'),
            APIField('office_hours'),
            APIField('slug'),
            APIField('seo_title'),
            APIField('search_description'),
            APIField('promote_image')
        ]

        template = 'page.html'

        parent_page_types = ['pages.HomePage']
        max_count = 1


class AnnualReportPage(Page):
    improving_access = StreamField([
        ('background_image', ImageBlock()),
        ('heading', blocks.CharBlock()),
        ('description', blocks.RichTextBlock()),
        ('give_text', blocks.CharBlock())
    ], null=True)
    revolution = StreamField([
        ('heading', blocks.CharBlock()),
        ('letter_body', blocks.RichTextBlock()),
        ('signature_image', ImageBlock()),
        ('signature_alt_text', blocks.CharBlock()),
        ('signature_text', blocks.RichTextBlock()),
        ('portrait', ImageBlock()),
        ('portrait_alt_text', blocks.CharBlock())
    ], null=True)
    founding = StreamField([
        ('caption', blocks.RichTextBlock()),
        ('portrait', ImageBlock()),
        ('portrait_alt_text', blocks.CharBlock()),
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
    ], null=True)
    reach = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.RichTextBlock()),
        ('facts', blocks.ListBlock(blocks.StructBlock([
            ('number', blocks.DecimalBlock()),
            ('unit', blocks.CharBlock()),
            ('text', blocks.CharBlock())
        ])))
    ], null=True)
    testimonials = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('testimonials', blocks.ListBlock(blocks.StructBlock([
            ('image', ImageBlock(required=False)),
            ('image_alt_text', blocks.CharBlock()),
            ('quote', blocks.CharBlock()),
            ('link', blocks.URLBlock()),
            ('link_text', blocks.CharBlock()),
        ])))
    ], null=True)
    sustainability = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('partners', blocks.ListBlock(blocks.StructBlock([
            ('image', ImageBlock(required=False)),
            ('image_alt_text', blocks.CharBlock()),
        ])))
    ], null=True)
    disruption = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('graph', blocks.StructBlock([
            ('top_caption', blocks.CharBlock()),
            ('bottom_caption', blocks.RichTextBlock()),
            ('image', ImageBlock(required=False)),
            ('image_alt_text', blocks.CharBlock(required=False)),
        ]))
    ], null=True)
    looking_ahead = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('image', ImageBlock()),
    ], null=True)
    map = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('link', blocks.CharBlock()),
        ('link_text', blocks.CharBlock()),
        ('background_image', ImageBlock()),
        ('image_1', ImageBlock()),
        ('image_2', ImageBlock()),
    ], null=True)
    tutor = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('link', blocks.CharBlock()),
        ('link_text', blocks.CharBlock()),
        ('right_image', ImageBlock()),
        ('bottom_image', ImageBlock()),
    ], null=True)
    philanthropic_partners = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('image', ImageBlock()),
        ('image_alt_text', blocks.CharBlock()),
        ('link_1', blocks.CharBlock()),
        ('link_1_text', blocks.CharBlock()),
        ('link_2', blocks.CharBlock()),
        ('link_2_text', blocks.CharBlock()),
        ('quote', blocks.TextBlock()),
        ('attribution_name', blocks.CharBlock()),
        ('attribution_title', blocks.CharBlock())

    ], null=True)
    giving = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('link', blocks.CharBlock()),
        ('link_text', blocks.CharBlock()),
    ], null=True)


    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        StreamFieldPanel('improving_access'),
        StreamFieldPanel('revolution'),
        StreamFieldPanel('founding'),
        StreamFieldPanel('reach'),
        StreamFieldPanel('testimonials'),
        StreamFieldPanel('sustainability'),
        StreamFieldPanel('disruption'),
        StreamFieldPanel('looking_ahead'),
        StreamFieldPanel('map'),
        StreamFieldPanel('tutor'),
        StreamFieldPanel('philanthropic_partners'),
        StreamFieldPanel('giving'),
    ]

    api_fields = [
        APIField('title'),
        APIField('improving_access'),
        APIField('revolution'),
        APIField('founding'),
        APIField('reach'),
        APIField('testimonials'),
        APIField('sustainability'),
        APIField('disruption'),
        APIField('looking_ahead'),
        APIField('map'),
        APIField('tutor'),
        APIField('philanthropic_partners'),
        APIField('giving'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']


class InstitutionalPartnership(Page):
    heading_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    heading_year = models.CharField(max_length=255)
    heading = models.CharField(max_length=255)
    program_tab_content = StreamField([
        ('tab', blocks.ListBlock(blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('description', blocks.RichTextBlock())
        ])))
    ], null=True)
    quote = models.TextField()
    quote_author = models.CharField(max_length=255)
    quote_title = models.CharField(max_length=255, blank=True, null=True)
    quote_school = models.CharField(max_length=255, blank=True, null=True)
    application_quote = models.TextField(blank=True, null=True)
    application_quote_author = models.CharField(max_length=255, blank=True, null=True)
    application_quote_title = models.CharField(max_length=255, blank=True, null=True)
    application_quote_school = models.CharField(max_length=255, blank=True, null=True)

    content_panels = [
        FieldPanel('title'),
        ImageChooserPanel('heading_image'),
        FieldPanel('heading_year'),
        FieldPanel('heading'),
        StreamFieldPanel('program_tab_content'),
        FieldPanel('quote'),
        FieldPanel('quote_author'),
        FieldPanel('quote_title'),
        FieldPanel('quote_school'),
        FieldPanel('application_quote'),
        FieldPanel('application_quote_author'),
        FieldPanel('application_quote_title'),
        FieldPanel('application_quote_school'),
    ]

    api_fields = [
        APIField('heading_image'),
        APIField('heading_year'),
        APIField('heading'),
        APIField('program_tab_content'),
        APIField('quote'),
        APIField('quote_author'),
        APIField('quote_title'),
        APIField('quote_school'),
        APIField('application_quote'),
        APIField('application_quote_author'),
        APIField('application_quote_title'),
        APIField('application_quote_school'),
        APIField('title'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    max_count = 1


class HeroJourneyPage(Page):
    books = StreamField([
        ('heading', blocks.CharBlock()),
        ('subheading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('book_heading', blocks.CharBlock()),
        ('book_description', blocks.TextBlock()),
        ('books_link', blocks.CharBlock()),
        ('books_link_text', blocks.CharBlock()),
        ('skip_html', blocks.RichTextBlock())
    ], null=True)
    quiz = StreamField([
        ('heading', blocks.CharBlock()),
        ('skip_link', blocks.CharBlock()),
        ('skip_link_text', blocks.CharBlock()),
        ('complete_message', blocks.CharBlock()),
        ('questions', blocks.ListBlock(blocks.StructBlock([
            ('question', blocks.CharBlock()),
            ('answers', blocks.ListBlock(blocks.StructBlock([
                ('text', blocks.CharBlock()),
                ('correct', blocks.BooleanBlock(required=False))
            ])
            ))
        ])))
    ], null=True)
    quiz_complete = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('instructions', blocks.TextBlock()),
        ('link_url', blocks.CharBlock()),
        ('link_text', blocks.CharBlock())
    ], null=True)
    share = StreamField([
        ('heading', blocks.CharBlock()),
        ('description', blocks.TextBlock()),
        ('instructions', blocks.TextBlock()),
    ], null=True)
    thanks = StreamField([
        ('heading', blocks.TextBlock()),
        ('description', blocks.TextBlock())
    ], null=True)


    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        StreamFieldPanel('books'),
        StreamFieldPanel('quiz'),
        StreamFieldPanel('quiz_complete'),
        StreamFieldPanel('share'),
        StreamFieldPanel('thanks'),
    ]

    api_fields = [
        APIField('title'),
        APIField('books'),
        APIField('quiz'),
        APIField('quiz_complete'),
        APIField('share'),
        APIField('thanks'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']


class InstitutionalPartnerProgramPage(Page):
    section_1_heading = models.CharField(max_length=255)
    section_1_description = RichTextField()
    section_1_link_text = models.CharField(max_length=255)
    section_1_link = models.URLField()
    section_1_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    quote = models.TextField()
    quote_name = models.CharField(max_length=255)
    quote_title = models.CharField(max_length=255)
    quote_school = models.CharField(max_length=255)
    section_2_heading = models.CharField(max_length=255)
    section_2_description = RichTextField()
    section_2_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_image_alt = models.CharField(max_length=255)
    section_3_heading = models.CharField(max_length=255)
    section_3_description = models.TextField()
    section_3_wide_cards = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('icon', ImageBlock()),
            ('html', blocks.RichTextBlock()),
        ])))
    ])
    section_3_tall_cards = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('html', blocks.RichTextBlock()),
            ('link', blocks.URLBlock()),
            ('link_text', blocks.CharBlock())
        ])))
    ])
    section_4_quote_text = models.TextField()
    section_4_quote_name = models.CharField(max_length=255)
    section_4_quote_title = models.CharField(max_length=255)
    section_4_quote_school = models.CharField(max_length=255, null=True)
    section_4_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_5_heading = models.CharField(max_length=255)
    section_5_description = RichTextField()
    section_5_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_5_image_alt = models.CharField(max_length=255)
    section_5_image_caption = models.CharField(max_length=255, null=True)
    section_6_heading = models.CharField(max_length=255)
    section_6_description = models.TextField()
    section_6_cards = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('heading_number', blocks.CharBlock()),
            ('heading_unit', blocks.CharBlock()),
            ('description', blocks.CharBlock())
        ])))
    ])
    section_7_heading = models.CharField(max_length=255)
    section_7_subheading = models.CharField(max_length=255)
    section_7_icons = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('image', ImageBlock()),
            ('image_alt_text', blocks.CharBlock()),
            ('current_cohort', blocks.BooleanBlock(required=False))
        ])))
    ])
    section_7_link_text = models.CharField(max_length=255)
    section_7_link_target = models.URLField()
    section_8_quote_text = models.TextField()
    section_8_quote_name = models.CharField(max_length=255)
    section_8_quote_title = models.CharField(max_length=255)
    section_8_quote_school = models.CharField(max_length=255)
    section_9_heading = models.CharField(max_length=255)
    section_9_submit_url = models.URLField()
    section_9_form_prompt = models.CharField(max_length=255)
    section_9_button_text = models.CharField(max_length=255)
    section_9_contact_html = RichTextField()

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('section_1_heading'),
        FieldPanel('section_1_description'),
        FieldPanel('section_1_link_text'),
        FieldPanel('section_1_link'),
        ImageChooserPanel('section_1_background_image'),
        FieldPanel('quote'),
        FieldPanel('quote_name'),
        FieldPanel('quote_title'),
        FieldPanel('quote_school'),
        FieldPanel('section_2_heading'),
        FieldPanel('section_2_description'),
        ImageChooserPanel('section_2_image'),
        FieldPanel('section_2_image_alt'),
        FieldPanel('section_3_heading'),
        FieldPanel('section_3_description'),
        StreamFieldPanel('section_3_wide_cards'),
        StreamFieldPanel('section_3_tall_cards'),
        FieldPanel('section_4_quote_text'),
        FieldPanel('section_4_quote_name'),
        FieldPanel('section_4_quote_title'),
        FieldPanel('section_4_quote_school'),
        ImageChooserPanel('section_4_background_image'),
        FieldPanel('section_5_heading'),
        FieldPanel('section_5_description'),
        ImageChooserPanel('section_5_image'),
        FieldPanel('section_5_image_alt'),
        FieldPanel('section_5_image_caption'),
        FieldPanel('section_6_heading'),
        FieldPanel('section_6_description'),
        StreamFieldPanel('section_6_cards'),
        FieldPanel('section_7_heading'),
        FieldPanel('section_7_subheading'),
        StreamFieldPanel('section_7_icons'),
        FieldPanel('section_7_link_text'),
        FieldPanel('section_7_link_target'),
        FieldPanel('section_8_quote_text'),
        FieldPanel('section_8_quote_name'),
        FieldPanel('section_8_quote_title'),
        FieldPanel('section_8_quote_school'),
        FieldPanel('section_9_heading'),
        FieldPanel('section_9_submit_url'),
        FieldPanel('section_9_form_prompt'),
        FieldPanel('section_9_button_text'),
        FieldPanel('section_9_contact_html'),
    ]

    api_fields = [
        APIField('title'),
        APIField('section_1_heading'),
        APIField('section_1_description'),
        APIField('section_1_link_text'),
        APIField('section_1_link'),
        APIField('section_1_background_image'),
        APIField('quote'),
        APIField('quote_name'),
        APIField('quote_title'),
        APIField('quote_school'),
        APIField('section_2_heading'),
        APIField('section_2_description'),
        APIField('section_2_image'),
        APIField('section_2_image_alt'),
        APIField('section_3_heading'),
        APIField('section_3_description'),
        APIField('section_3_wide_cards'),
        APIField('section_3_tall_cards'),
        APIField('section_4_quote_text'),
        APIField('section_4_quote_name'),
        APIField('section_4_quote_title'),
        APIField('section_4_quote_school'),
        APIField('section_4_background_image'),
        APIField('section_5_heading'),
        APIField('section_5_description'),
        APIField('section_5_image'),
        APIField('section_5_image_alt'),
        APIField('section_5_image_caption'),
        APIField('section_6_heading'),
        APIField('section_6_description'),
        APIField('section_6_cards'),
        APIField('section_7_heading'),
        APIField('section_7_subheading'),
        APIField('section_7_icons'),
        APIField('section_7_link_text'),
        APIField('section_7_link_target'),
        APIField('section_8_quote_text'),
        APIField('section_8_quote_name'),
        APIField('section_8_quote_title'),
        APIField('section_8_quote_school'),
        APIField('section_9_heading'),
        APIField('section_9_submit_url'),
        APIField('section_9_form_prompt'),
        APIField('section_9_button_text'),
        APIField('section_9_contact_html'),
    ]

    parent_page_type = ['pages.HomePage']


class CreatorFestPage(Page):
    banner_headline = models.CharField(max_length=255)
    banner_content = RichTextField()
    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    register = StreamField([
        ('box', blocks.ListBlock(blocks.StructBlock([
            ('headline', blocks.CharBlock()),
            ('address', blocks.RichTextBlock()),
            ('button_url', blocks.URLBlock()),
            ('button_text', blocks.CharBlock()),
        ])))
    ])
    navigator = StreamField([
        ('menu_item', blocks.ListBlock(blocks.StructBlock([
            ('text', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True)

    page_panels = StreamField([
        ('panel', blocks.StructBlock([
            ('superheading', blocks.CharBlock(required=False)),
            ('heading', blocks.CharBlock()),
            ('background_image', ImageBlock(required=False)),
            ('embed', blocks.RawHTMLBlock(required=False)),
            ('paragraph', blocks.RichTextBlock(required=False)),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('icon', ImageBlock()),
                ('headline', blocks.CharBlock()),
                ('description', blocks.RichTextBlock())
            ], null=True)
            ))
        ]))
    ], null=True)

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('banner_headline'),
        FieldPanel('banner_content'),
        ImageChooserPanel('banner_image'),
        StreamFieldPanel('register'),
        StreamFieldPanel('navigator'),
        StreamFieldPanel('page_panels'),
    ]

    api_fields = [
        APIField('title'),
        APIField('banner_headline'),
        APIField('banner_content'),
        APIField('banner_image'),
        APIField('register'),
        APIField('navigator'),
        APIField('page_panels'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']


class PartnersPage(Page):
    heading = models.CharField(max_length=255)
    description = RichTextField()
    partner_landing_page_link = models.CharField(max_length=255, null=True, blank=True, help_text="Link text to partner landing page.")
    partner_request_info_link = models.CharField(max_length=255, null=True, blank=True, help_text="Forstack form link text")

    @staticmethod
    def category_mapping():
        field_mappings = PartnerCategoryMapping.objects.all()
        mapping_dict = {}

        for field in field_mappings:
            mapping_dict[field.display_name] = field.salesforce_name

        return mapping_dict

    @staticmethod
    def field_name_mapping():
        field_mappings = PartnerFieldNameMapping.objects.filter(hidden=False)
        mapping_dict = {}

        for field in field_mappings:
            mapping_dict[field.display_name] = field.salesforce_name

        return mapping_dict

    @staticmethod
    def partner_type_choices():
        return [x.display_name for x in PartnerTypeMapping.objects.all()]

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('partner_landing_page_link'),
        FieldPanel('partner_request_info_link'),
    ]

    api_fields = [
        APIField('title'),
        APIField('heading'),
        APIField('description'),
        APIField('partner_landing_page_link'),
        APIField('partner_request_info_link'),
        APIField('category_mapping'),
        APIField('field_name_mapping'),
        APIField('partner_type_choices'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']

class WebinarPage(Page):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('description'),
        ImageChooserPanel('hero_image')
    ]

    api_fields = [
        APIField('title'),
        APIField('heading'),
        APIField('description'),
        APIField('hero_image'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']


class PartnerChooserBlock(blocks.ChooserBlock):
    target_model = Partner
    widget = forms.Select

    # Return the key value for the select field
    def value_for_form(self, value):
        if isinstance(value, self.target_model):
            return value.pk
        else:
            return value

    def get_api_representation(self, value, context=None):
        if value.partner_logo:
            return {
                'id': value.id,
                'name': value.partner_name,
                'logo': value.partner_logo.url
            }
        else:
            return {
                'id': value.id,
                'name': value.partner_name,
                'logo': None
            }

class MathQuizPage(Page):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    results = StreamField([
        ('result', blocks.ListBlock(blocks.StructBlock([
            ('image', ImageBlock()),
            ('headline', blocks.CharBlock()),
            ('description', blocks.TextBlock()),
            ('partners', blocks.ListBlock(blocks.StructBlock([
                ('partner', PartnerChooserBlock()),
             ]))),
        ])))
    ])

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('description'),
        StreamFieldPanel('results')
    ]

    api_fields = [
        APIField('title'),
        APIField('heading'),
        APIField('description'),
        APIField('results'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
