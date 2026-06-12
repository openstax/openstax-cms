from django.db import models
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.api import APIField

from openstax.api_fields import ExpandedRichTextField
from openstax.preview import FrontendPreviewMixin






class TermsOfService(FrontendPreviewMixin, Page):
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
        APIField('terms_of_service_content', serializer=ExpandedRichTextField()),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('terms_of_service_content'),
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


class Accessibility(FrontendPreviewMixin, Page):
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
        APIField('accessibility_content', serializer=ExpandedRichTextField()),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('accessibility_content'),
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


class Licensing(FrontendPreviewMixin, Page):
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
        APIField('licensing_content', serializer=ExpandedRichTextField()),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('licensing_content'),
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


class PrivacyPolicy(FrontendPreviewMixin, Page):
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
        APIField('privacy_content', serializer=ExpandedRichTextField()),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('privacy_content'),
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


