from django.db import models
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.api import APIField

from openstax.api_fields import ExpandedRichTextField
from openstax.functions import build_document_url
from openstax.preview import FrontendPreviewMixin

from pages.custom_blocks import APIImageChooserBlock, \
    FAQBlock, \
    AllyLogoBlock, \
    AssignableBookBlock




class WebinarPage(FrontendPreviewMixin, Page):
    heading = models.CharField(max_length=255)

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
    ]

    api_fields = [
        APIField('title'),
        APIField('heading'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_types = ['pages.RootPage']
    template = 'page.html'


class AllyLogos(FrontendPreviewMixin, Page):
    heading = models.CharField(max_length=255)
    description = RichTextField()
    ally_logos_heading = models.CharField(max_length=255)
    ally_logos_description = RichTextField()
    ally_logos = StreamField([
        ('ally_logo', blocks.ListBlock(AllyLogoBlock())),
    ], use_json_field=True)
    book_ally_logos_heading = models.CharField(max_length=255)
    book_ally_logos_description = RichTextField()
    book_ally_logos = StreamField([
        ('book_ally_logo', blocks.ListBlock(AllyLogoBlock())),
    ], use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        TitleFieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('ally_logos_heading'),
        FieldPanel('ally_logos_description'),
        FieldPanel('ally_logos'),
        FieldPanel('book_ally_logos_heading'),
        FieldPanel('book_ally_logos_description'),
        FieldPanel('book_ally_logos')
    ]

    api_fields = [
        APIField('heading'),
        APIField('description', serializer=ExpandedRichTextField()),
        APIField('ally_logos_heading'),
        APIField('ally_logos_description', serializer=ExpandedRichTextField()),
        APIField('ally_logos'),
        APIField('book_ally_logos_heading'),
        APIField('book_ally_logos_description', serializer=ExpandedRichTextField()),
        APIField('book_ally_logos'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'
    parent_page_types = ['pages.RootPage']


class Assignable(FrontendPreviewMixin, Page):
    heading_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    heading_title_image = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Title to be displayed on the page. Should be an svg file.'
    )

    def get_heading_title_image_url(self):
        return build_document_url(self.heading_title_image.url)

    heading_title_image_url = property(get_heading_title_image_url)
    subheading = models.CharField(max_length=255, blank=True, null=True)
    heading_description = RichTextField(blank=True, null=True)
    add_assignable_cta_header = models.CharField(max_length=255, blank=True, null=True)
    add_assignable_cta_description = models.TextField(blank=True, null=True)
    add_assignable_cta_link = models.URLField(blank=True, null=True)
    add_assignable_cta_button_text = models.CharField(max_length=255, blank=True, null=True)
    instructor_interest_cta_header = models.CharField(max_length=255, blank=True, null=True)
    instructor_interest_cta_description = models.TextField(blank=True, null=True)
    instructor_interest_cta_link = models.URLField(blank=True, null=True)
    instructor_interest_cta_button_text = models.CharField(max_length=255, blank=True, null=True)
    instructor_help_cta_header = models.CharField(max_length=255, blank=True, null=True)
    instructor_help_cta_description = models.TextField(blank=True, null=True)
    instructor_help_cta_link = models.URLField(blank=True, null=True)
    instructor_help_cta_button_text = models.CharField(max_length=255, blank=True, null=True)
    cta_section_footer = RichTextField(blank=True, null=True)
    available_courses_header = models.CharField(max_length=255, blank=True, null=True)
    available_books = StreamField([
        ('course', AssignableBookBlock()),
    ], null=True, blank=True, use_json_field=True)
    courses_coming_soon_header = models.CharField(max_length=255, blank=True, null=True)
    coming_soon_books = StreamField([
        ('course', AssignableBookBlock()),
    ], null=True, blank=True, use_json_field=True)
    assignable_cta_text = models.CharField(max_length=255, blank=True, null=True)
    assignable_cta_link = models.URLField(blank=True, null=True)
    assignable_cta_button_text = models.CharField(max_length=255, blank=True, null=True)
    section_2_heading = models.CharField(max_length=255, blank=True, null=True)
    section_2_description = models.TextField(blank=True, null=True)
    image_carousel = StreamField(
        blocks.StreamBlock([
            ('carousel_image', blocks.ListBlock(blocks.StructBlock([
                ('image', APIImageChooserBlock(required=False)),
            ])))]), blank=True, null=True, use_json_field=True)
    faq_header = models.CharField(max_length=255, blank=True, null=True)
    faqs = StreamField([
        ('faq', FAQBlock()),
    ], blank=True, null=True, use_json_field=True)
    quote = models.TextField(blank=True, null=True)
    quote_author = models.CharField(max_length=255, blank=True, null=True)
    quote_title = models.CharField(max_length=255, blank=True, null=True)
    quote_school = models.CharField(max_length=255, blank=True, null=True)
    tos_link = models.URLField(blank=True, null=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        TitleFieldPanel('title'),
        FieldPanel('heading_image'),
        FieldPanel('heading_title_image'),
        FieldPanel('subheading'),
        FieldPanel('heading_description'),
        FieldPanel('add_assignable_cta_header'),
        FieldPanel('add_assignable_cta_description'),
        FieldPanel('add_assignable_cta_link'),
        FieldPanel('add_assignable_cta_button_text'),
        FieldPanel('instructor_interest_cta_header'),
        FieldPanel('instructor_interest_cta_description'),
        FieldPanel('instructor_interest_cta_link'),
        FieldPanel('instructor_interest_cta_button_text'),
        FieldPanel('instructor_help_cta_header'),
        FieldPanel('instructor_help_cta_description'),
        FieldPanel('instructor_help_cta_link'),
        FieldPanel('instructor_help_cta_button_text'),
        FieldPanel('cta_section_footer'),
        FieldPanel('available_courses_header'),
        FieldPanel('available_books'),
        FieldPanel('courses_coming_soon_header'),
        FieldPanel('coming_soon_books'),
        FieldPanel('assignable_cta_text'),
        FieldPanel('assignable_cta_link'),
        FieldPanel('assignable_cta_button_text'),
        FieldPanel('section_2_heading'),
        FieldPanel('section_2_description'),
        FieldPanel('image_carousel'),
        FieldPanel('faq_header'),
        FieldPanel('faqs'),
        FieldPanel('quote'),
        FieldPanel('quote_author'),
        FieldPanel('quote_title'),
        FieldPanel('quote_school'),
        FieldPanel('tos_link'),
    ]

    api_fields = [
        APIField('title'),
        APIField('heading_image'),
        APIField('heading_title_image_url'),
        APIField('subheading'),
        APIField('heading_description', serializer=ExpandedRichTextField()),
        APIField('add_assignable_cta_header'),
        APIField('add_assignable_cta_description'),
        APIField('add_assignable_cta_link'),
        APIField('add_assignable_cta_button_text'),
        APIField('instructor_interest_cta_header'),
        APIField('instructor_interest_cta_description'),
        APIField('instructor_interest_cta_link'),
        APIField('instructor_interest_cta_button_text'),
        APIField('instructor_help_cta_header'),
        APIField('instructor_help_cta_description'),
        APIField('instructor_help_cta_link'),
        APIField('instructor_help_cta_button_text'),
        APIField('cta_section_footer', serializer=ExpandedRichTextField()),
        APIField('available_courses_header'),
        APIField('available_books'),
        APIField('courses_coming_soon_header'),
        APIField('coming_soon_books'),
        APIField('assignable_cta_text'),
        APIField('assignable_cta_link'),
        APIField('assignable_cta_button_text'),
        APIField('section_2_heading'),
        APIField('section_2_description'),
        APIField('image_carousel'),
        APIField('faq_header'),
        APIField('faqs'),
        APIField('quote'),
        APIField('quote_author'),
        APIField('quote_title'),
        APIField('quote_school'),
        APIField('tos_link'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    parent_page_types = ['pages.RootPage']
    template = 'page.html'
    max_count = 1
