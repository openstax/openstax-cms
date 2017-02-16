from django import forms
from django.db import models
from django.http.response import JsonResponse
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                StreamFieldPanel)
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks import FieldBlock, RawHTMLBlock, StructBlock
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from openstax.functions import build_image_url

from allies.models import Ally


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


class StrategicAdvisors(models.Model):
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


class OpenStaxTeam(models.Model):
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
        'books.BookIndex',
        'news.NewsIndex',
        'allies.Ally',
    ]


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

    ]

    parent_page_types = ['pages.HomePage']


class ContactUs(Page):
    tagline = models.CharField(max_length=255)
    mailing_header = models.CharField(max_length=255)
    mailing_address = RichTextField()
    customer_service = RichTextField()

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
    page_description = models.TextField()

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

    ]

    parent_page_types = ['pages.HomePage']


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
    description = models.TextField()

    api_fields = ('title', 'funder_logo', 'description', )

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('logo'),
        FieldPanel('description'),
    ]


class FoundationSupportFunders(Orderable, Funder):
    page = ParentalKey('pages.FoundationSupport', related_name='funders')


class FoundationSupport(Page):
    page_description = models.TextField()

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

    ]

    parent_page_types = ['pages.HomePage']


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


class OurImpactInstitutions(Orderable, Institutions):
    page = ParentalKey('pages.OurImpact', related_name='institutions')


class OurImpact(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()

    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])

    api_fields = (
        'title',
        'intro_heading',
        'intro_description',
        'institutions',
        'slug',
        'seo_title',
        'search_description',
    )

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
    ]

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
    ]

    parent_page_types = ['pages.HomePage']


class TermsOfService(Page):
    intro_heading = models.CharField(max_length=255)
    terms_of_service_content = RichTextField()

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
    ]

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
    ]

    parent_page_types = ['pages.HomePage']


class FAQ(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()

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
    ]

    parent_page_types = ['pages.HomePage']


class Support(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()

    row_1 = StreamField([
        ('column', ColumnBlock()),
    ])

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
    ]

    parent_page_types = ['pages.HomePage']


class GiveForm(Page):
    page_description = models.TextField()

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
    ]

    parent_page_types = ['pages.HomePage']


class Accessibility(Page):
    intro_heading = models.CharField(max_length=255)
    accessibility_content = RichTextField()

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
    ]

    parent_page_types = ['pages.HomePage']


class Licensing(Page):
    intro_heading = models.CharField(max_length=255)
    licensing_content = RichTextField()

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
    ]

    parent_page_types = ['pages.HomePage']
