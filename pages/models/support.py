from django.db import models
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.api import APIField

from openstax.api_fields import ExpandedRichTextField
from openstax.preview import FrontendPreviewMixin


from pages.custom_blocks import FAQBlock, \
    BookProviderBlock




class ContactUs(FrontendPreviewMixin, Page):
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
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('tagline'),
        FieldPanel('mailing_header'),
        FieldPanel('mailing_address'),
        FieldPanel('customer_service'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')

    ]

    api_fields = [
        APIField('title'),
        APIField('tagline'),
        APIField('mailing_header'),
        APIField('mailing_address', serializer=ExpandedRichTextField()),
        APIField('customer_service', serializer=ExpandedRichTextField()),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class FAQ(FrontendPreviewMixin, Page):
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
    ], use_json_field=True)

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description', serializer=ExpandedRichTextField()),
        APIField('questions'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('questions'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage', 'pages.RootPage']


class ErrataList(FrontendPreviewMixin, Page):
    correction_schedule = RichTextField()
    deprecated_errata_message = RichTextField(
        help_text="Errata message for deprecated books, controlled via the book state field.")
    new_edition_errata_message = RichTextField(
        help_text="Errata message for books with new editions, controlled via the book state field.")
    about_header = models.CharField(max_length=255, help_text="About our correction schedule")
    about_text = RichTextField(help_text="Errata received from March through...\" the stuff that will show on the page")
    about_popup = RichTextField(help_text="Instructor and student resources...\" the stuff that will be in the popup")

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('correction_schedule', serializer=ExpandedRichTextField()),
        APIField('deprecated_errata_message', serializer=ExpandedRichTextField()),
        APIField('new_edition_errata_message', serializer=ExpandedRichTextField()),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
        APIField('about_header'),
        APIField('about_text', serializer=ExpandedRichTextField()),
        APIField('about_popup', serializer=ExpandedRichTextField())
    ]

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('correction_schedule'),
        FieldPanel('deprecated_errata_message'),
        FieldPanel('new_edition_errata_message'),
        FieldPanel('about_header'),
        FieldPanel('about_text'),
        FieldPanel('about_popup')
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1

    def get_sitemap_urls(self, request=None):
        return []


class PrintOrder(FrontendPreviewMixin, Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = models.TextField()
    featured_provider_intro_blurb = models.TextField()
    featured_providers = StreamField([
        ('provider', BookProviderBlock(icon='document')),
    ], null=True, use_json_field=True)
    other_providers_intro_blurb = models.TextField()
    providers = StreamField([
        ('provider', BookProviderBlock(icon='document')),
    ], use_json_field=True)

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
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('featured_provider_intro_blurb'),
        FieldPanel('featured_providers'),
        FieldPanel('other_providers_intro_blurb'),
        FieldPanel('providers'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class FormHeadings(FrontendPreviewMixin, Page):
    LOGGED_IN_HELP = (
        'Optional. Shown to logged-in users instead of the default. '
        'Supports tags: {{first_name}}, {{last_name}}, {{school}}.'
    )

    adoption_intro_heading = models.CharField(max_length=255)
    adoption_intro_description = RichTextField()
    adoption_logged_in_intro_heading = models.CharField(
        max_length=255, blank=True, default='', help_text=LOGGED_IN_HELP
    )
    adoption_logged_in_intro_description = RichTextField(
        blank=True, default='', help_text=LOGGED_IN_HELP
    )
    interest_intro_heading = models.CharField(max_length=255)
    interest_intro_description = RichTextField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('adoption_intro_heading'),
        APIField('adoption_intro_description', serializer=ExpandedRichTextField()),
        APIField('adoption_logged_in_intro_heading'),
        APIField('adoption_logged_in_intro_description', serializer=ExpandedRichTextField()),
        APIField('interest_intro_heading'),
        APIField('interest_intro_description', serializer=ExpandedRichTextField()),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title'),
        FieldPanel('adoption_intro_heading'),
        FieldPanel('adoption_intro_description'),
        FieldPanel('adoption_logged_in_intro_heading'),
        FieldPanel('adoption_logged_in_intro_description'),
        FieldPanel('interest_intro_heading'),
        FieldPanel('interest_intro_description')
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


