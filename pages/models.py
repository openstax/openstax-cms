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

from allies.models import Ally
from books.models import Book
from api.serializers import ImageSerializer


### Custom Block Definitions ###

class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),))


class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    alt_text = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    alignment = ImageFormatChoiceBlock()


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

    class Meta:
        icon = 'document'

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'name': value['name'],
                'blurb': value['blurb'],
                'icon': build_image_url(value['icon']),
                'cta': value['cta'],
                'url': value['url']
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

class RoverCardsSection2(Orderable, Card):
    rover_cards = ParentalKey('pages.Rover', related_name='rover_cards_section_2')

class RoverCardsSection3(Orderable, Card):
    rover_cards = ParentalKey('pages.Rover', related_name='rover_cards_section_3')


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
    where_map_url = property(get_where_map)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = (
        'who_heading',
        'who_paragraph',
        'who_image',
        'who_image_url',
        'what_heading',
        'what_paragraph',
        'what_cards',
        'where_heading',
        'where_paragraph',
        'where_map',
        'where_map_url',
        'slug',
        'seo_title',
        'search_description',)

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
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']


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

    api_fields = (
        'title',
        'header',
        'subheader',
        'header_image_url',
        'team_header',
        'openstax_people',
        'slug',
        'seo_title',
        'search_description',)

    template = 'page.html'


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

    api_fields = (
        'title',
        'mobile_banner_images',
        'banner_images',
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
        'pages.EcosystemAllies',
        'pages.FoundationSupport',
        'pages.OurImpact',
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
        'pages.Rover',
        'books.BookIndex',
        'news.NewsIndex',
        'news.PressIndex',
        'allies.Ally',
    ]

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
        'get_started_step_2_logged_in_cta',
        'get_started_step_2_logged_out_cta',
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

    api_fields = (
        'title',
        'tagline',
        'mailing_header',
        'mailing_address',
        'customer_service',
        'slug',
        'seo_title',
        'search_description',
    )

    template = 'page.html'

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
        ('html', RawHTMLBlock()),
    ])
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

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
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

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
    page_description = models.TextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def allies(self):
        allies = Ally.objects.all()
        ally_data = {}
        for ally in allies:
            ally_data[ally.slug] = {
                'title': ally.title,
                'subjects': ally.ally_subject_list(),
                'short_description': ally.short_description,
                'long_description': ally.long_description,
                'heading': ally.heading,
                'is_ap': ally.is_ap,
                'do_not_display': ally.do_not_display,
                'ally_bw_logo': ally.ally_bw_logo,
            }
        return ally_data

    api_fields = (
        'title',
        'page_description',
        'allies',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('page_description'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image'),
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']


class FoundationSupport(Page):
    page_description = models.TextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = (
        'title',
        'page_description',
        'funders',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
        'other_payment_methods_heading',
        'payment_method_1_heading',
        'payment_method_1_content',
        'payment_method_2_heading',
        'payment_method_2_content',
        'payment_method_3_heading',
        'payment_method_3_content',
        'payment_method_4_heading',
        'payment_method_4_content',
        'give_cta',
        'give_cta_link',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'title',
        'intro_heading',
        'terms_of_service_content',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
        'row_1',
        'row_2',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
        'questions',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
        'row_1',
    )

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


class GiveForm(Page):
    page_description = models.TextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = (
        'title',
        'page_description',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'title',
        'intro_heading',
        'accessibility_content',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'title',
        'intro_heading',
        'licensing_content',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
    )

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

    api_fields = (
        'title',
        'pop_up_text',
        'access_tagline',
        'access_button_cta',
        'access_button_link',
        'section_1_heading',
        'section_1_subheading',
        'section_1_paragraph',
        'section_1_cta_link',
        'section_1_cta_text',
        'section_2_heading',
        'section_2_subheading',
        'section_2_paragraph',
        'icon_1_image_url',
        'icon_1_subheading',
        'icon_1_paragraph',
        'icon_2_image_url',
        'icon_2_subheading',
        'icon_2_paragraph',
        'icon_3_image_url',
        'icon_3_subheading',
        'icon_3_paragraph',
        'icon_4_image_url',
        'icon_4_subheading',
        'icon_4_paragraph',
        'section_3_heading',
        'section_3_paragraph',
        'marketing_videos',
        'resource_availability',
        'section_4_heading',
        'section_4_paragraph',
        'section_4_resource_fine_print',
        'marketing_books',
        'section_4_book_heading',
        'section_4_coming_soon_heading',
        'section_4_coming_soon_text',
        'section_5_heading',
        'section_5_paragraph',
        'section_5_science_heading',
        'section_5_science_paragraph',
        'section_6_heading',
        'section_6_knowledge_base_copy',
        'faqs',
        'section_7_heading',
        'section_7_subheading',
        'section_7_cta_text_1',
        'section_7_cta_link_1',
        'section_7_cta_blurb_1',
        'section_7_cta_text_2',
        'section_7_cta_link_2',
        'section_7_cta_blurb_2',
        'floating_footer_button_1_cta',
        'floating_footer_button_1_link',
        'floating_footer_button_1_caption',
        'floating_footer_button_2_cta',
        'floating_footer_button_2_link',
        'floating_footer_button_2_caption',
        'slug',
        'seo_title',
        'search_description',
    )

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

    api_fields = (
        'intro_heading',
        'intro_description',
        'banner_cta',
        'banner_cta_link',
        'select_tech_heading',
        'select_tech_step_1',
        'select_tech_step_2',
        'select_tech_step_3',
        'new_frontier_heading',
        'new_frontier_subheading',
        'new_frontier_description',
        'new_frontier_cta_1',
        'new_frontier_cta_link_1',
        'new_frontier_cta_2',
        'new_frontier_cta_link_2')

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


class ErrataList(Page):
    correction_schedule = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = (
        'correction_schedule',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('correction_schedule')
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']


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

    api_fields = (
        'title',
        'intro_heading',
        'privacy_content',
        'slug',
        'seo_title',
        'search_description',
    )

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
    isbn_download = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def get_isbn_download(self):
        return build_document_url(self.isbn_download.url)

    isbn_download_url = property(get_isbn_download)
    isbn_cta = models.CharField(max_length=255)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = (
        'title',
        'intro_heading',
        'intro_description',
        'featured_provider_intro_blurb',
        'featured_providers',
        'other_providers_intro_blurb',
        'providers',
        'isbn_download_url',
        'isbn_cta',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('featured_provider_intro_blurb'),
        StreamFieldPanel('featured_providers'),
        FieldPanel('other_providers_intro_blurb'),
        StreamFieldPanel('providers'),
        FieldPanel('isbn_download'),
        FieldPanel('isbn_cta'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']


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
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']


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

    api_fields = (
        'title',
        'intro_heading',
        'careers_content',
        'slug',
        'seo_title',
        'search_description',
    )

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


class Rover(Page):
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_header_image(self):
        return build_document_url(self.header_image.url)
    header_image_url = property(get_header_image)

    header_image_alt = models.CharField(max_length=255)
    mobile_header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    def get_mobile_header_image(self):
        return build_document_url(self.mobile_header_image.url)
    mobile_header_image_url = property(get_mobile_header_image)

    section_1_headline = models.CharField(max_length=255, null=True)
    section_1_description = RichTextField(null=True)
    section_1_button_text = models.CharField(max_length=255, null=True)
    section_1_button_url = models.URLField(null=True)

    section_2_headline = models.CharField(max_length=255, null=True)
    #section 2 cards are an inline panel
    
    section_3_headline = models.CharField(max_length=255, null=True)
    section_3_description = models.TextField(null=True)
    #section 3 cards are an inline panel

    form_headline = models.CharField(max_length=255)

    section_4_headline = models.CharField(max_length=255, null=True)
    section_4_faqs = StreamField([
        ('headline', blocks.CharBlock()),
        ('faqs', blocks.ListBlock(blocks.StructBlock([
            ('question', blocks.CharBlock()),
            ('answer', blocks.TextBlock())
        ]))),
    ], null=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        ImageChooserPanel('header_image'),
        FieldPanel('header_image_alt'),
        ImageChooserPanel('mobile_header_image'),
        FieldPanel('section_1_headline'),
        FieldPanel('section_1_description'),
        FieldPanel('section_1_button_text'),
        FieldPanel('section_1_button_url'),
        FieldPanel('section_2_headline'),
        InlinePanel('rover_cards_section_2', label='Section 2 Cards'),
        FieldPanel('section_3_headline'),
        FieldPanel('section_3_description'),
        InlinePanel('rover_cards_section_3', label='Section 3 Cards'),
        FieldPanel('form_headline'),
        FieldPanel('section_4_headline'),
        StreamFieldPanel('section_4_faqs'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')

    ]

    api_fields = [
        APIField('header_image_url'),
        APIField('header_image_alt'),
        APIField('mobile_header_image_url'),
        APIField('section_1_headline'),
        APIField('section_1_description'),
        APIField('section_1_button_text'),
        APIField('section_1_button_url'),
        APIField('section_2_headline'),
        APIField('rover_cards_section_2'),
        APIField('section_3_headline'),
        APIField('section_3_description'),
        APIField('rover_cards_section_3'),
        APIField('form_headline'),
        APIField('section_4_headline'),
        APIField('section_4_faqs'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']



