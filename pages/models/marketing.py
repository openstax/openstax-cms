from django import forms
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
from books.models import Book
from webinars.models import Webinar

from salesforce.models import Partner

from pages.custom_blocks import ImageBlock, \
    APIImageChooserBlock, \
    FAQBlock, \
    CardBlock, \
    CardImageBlock, \
    AllyLogoBlock, \
    AssignableBookBlock, \
    APIRichTextBlock




class CreatorFestPage(FrontendPreviewMixin, Page):
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
            ('address', APIRichTextBlock()),
            ('button_url', blocks.URLBlock()),
            ('button_text', blocks.CharBlock()),
        ])))
    ], use_json_field=True)
    navigator = StreamField([
        ('menu_item', blocks.ListBlock(blocks.StructBlock([
            ('text', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, use_json_field=True)

    page_panels = StreamField([
        ('panel', blocks.StructBlock([
            ('superheading', blocks.CharBlock(required=False)),
            ('heading', blocks.CharBlock()),
            ('background_image', ImageBlock(required=False)),
            ('embed', blocks.RawHTMLBlock(required=False)),
            ('paragraph', APIRichTextBlock(required=False)),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('icon', ImageBlock()),
                ('headline', blocks.CharBlock()),
                ('description', APIRichTextBlock())
            ], null=True)
            ))
        ]))
    ], null=True, use_json_field=True)

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('banner_headline'),
        FieldPanel('banner_content'),
        FieldPanel('banner_image'),
        FieldPanel('register'),
        FieldPanel('navigator'),
        FieldPanel('page_panels'),
    ]

    api_fields = [
        APIField('title'),
        APIField('banner_headline'),
        APIField('banner_content', serializer=ExpandedRichTextField()),
        APIField('banner_image'),
        APIField('register'),
        APIField('navigator'),
        APIField('page_panels'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    template = 'page.html'


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

    parent_page_type = ['pages.HomePage']
    template = 'page.html'


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


class MathQuizPage(FrontendPreviewMixin, Page):
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
    ], use_json_field=True)

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('results')
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


class LLPHPage(FrontendPreviewMixin, Page):
    heading = models.CharField(max_length=255)
    subheading = models.TextField()
    hero_background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    signup_link_href = models.URLField()
    signup_link_text = models.CharField(max_length=255)
    book_cover = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The book cover to be shown on the website.'
    )

    def get_book_cover(self):
        return build_document_url(self.book_cover.url)

    book_cover_url = property(get_book_cover)

    info_link_slug = models.CharField(max_length=255, default="/details/books/life-liberty-and-pursuit-happiness")
    info_link_text = models.CharField(max_length=255, default="Not an educator? Take a look at the book here.")
    book_heading = models.CharField(max_length=255)
    book_description = RichTextField()

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('hero_background'),
        FieldPanel('signup_link_href'),
        FieldPanel('signup_link_text'),
        FieldPanel('book_cover'),
        FieldPanel('info_link_slug'),
        FieldPanel('info_link_text'),
        FieldPanel('book_heading'),
        FieldPanel('book_description')
    ]

    api_fields = [
        APIField('title'),
        APIField('heading'),
        APIField('subheading'),
        APIField('hero_background'),
        APIField('signup_link_href'),
        APIField('signup_link_text'),
        APIField('book_cover_url'),
        APIField('info_link_slug'),
        APIField('info_link_text'),
        APIField('book_heading'),
        APIField('book_description', serializer=ExpandedRichTextField()),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    template = 'page.html'

    class Meta:
        verbose_name = "LLPH Page"


class TutorMarketing(FrontendPreviewMixin, Page):
    # header section
    header = models.CharField(max_length=255)
    description = models.TextField()
    header_cta_button_text = models.CharField(max_length=255)
    header_cta_button_link = models.URLField()
    quote = RichTextField()

    # features
    features_header = models.CharField(max_length=255)
    features_cards = StreamField([
        ('cards', CardImageBlock()),
    ], use_json_field=True)

    # availble books
    available_books_header = models.CharField(max_length=255)

    # cost
    cost_header = models.CharField(max_length=255)
    cost_description = models.TextField()
    cost_cards = StreamField([
        ('cards', CardBlock()),
    ], use_json_field=True)
    cost_institution_message = models.CharField(max_length=255)

    # feedback
    feedback_media = StreamField(
        blocks.StreamBlock([
            ('image', ImageBlock()),
            ('video', blocks.RawHTMLBlock())
        ], max_num=1), use_json_field=True)
    feedback_heading = models.CharField(max_length=255)
    feedback_quote = models.TextField()
    feedback_name = models.CharField(max_length=255)
    feedback_occupation = models.CharField(max_length=255)
    feedback_organization = models.CharField(max_length=255)

    # webinars
    webinars_header = models.CharField(max_length=255)

    # faq
    faq_header = models.CharField(max_length=255)
    faqs = StreamField([
        ('faq', FAQBlock()),
    ], use_json_field=True)

    demo_cta_text = models.CharField(max_length=255)
    demo_cta_link = models.URLField()
    tutor_login_link = models.URLField()
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def tutor_books(self):
        books = Book.objects.filter(tutor_marketing_book=True).order_by('path')
        book_data = []
        for book in books:
            if book.book_state not in ['Retired', 'Draft']:
                book_data.append({
                    'id': book.id,
                    'slug': 'books/{}'.format(book.slug),
                    'title': book.title,
                    'cover_url': book.cover_url,
                })
        return book_data

    @property
    def webinars(self):
        webinars = Webinar.objects.filter(display_on_tutor_page=True)
        webinar_data = []
        for webinar in webinars:
            webinar_data.append({
                'id': webinar.id,
                'title': webinar.title,
                'description': webinar.description,
                'link': webinar.registration_url,
            })
        return webinar_data

    api_fields = [
        APIField('title'),
        APIField('header'),
        APIField('description'),
        APIField('header_cta_button_text'),
        APIField('header_cta_button_link'),
        APIField('quote', serializer=ExpandedRichTextField()),
        APIField('features_header'),
        APIField('features_cards'),
        APIField('available_books_header'),
        APIField('tutor_books'),
        APIField('cost_header'),
        APIField('cost_description'),
        APIField('cost_cards'),
        APIField('cost_institution_message'),
        APIField('feedback_media'),
        APIField('feedback_heading'),
        APIField('feedback_quote'),
        APIField('feedback_name'),
        APIField('feedback_occupation'),
        APIField('feedback_organization'),
        APIField('webinars_header'),
        APIField('webinars'),
        APIField('faq_header'),
        APIField('faqs'),
        APIField('demo_cta_text'),
        APIField('demo_cta_link'),
        APIField('tutor_login_link'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('header'),
        FieldPanel('description'),
        FieldPanel('header_cta_button_text'),
        FieldPanel('header_cta_button_link'),
        FieldPanel('quote'),
        FieldPanel('features_header'),
        FieldPanel('features_cards'),
        FieldPanel('available_books_header'),
        FieldPanel('cost_header'),
        FieldPanel('cost_description'),
        FieldPanel('cost_cards'),
        FieldPanel('cost_institution_message'),
        FieldPanel('feedback_media'),
        FieldPanel('feedback_heading'),
        FieldPanel('feedback_quote'),
        FieldPanel('feedback_name'),
        FieldPanel('feedback_occupation'),
        FieldPanel('feedback_organization'),
        FieldPanel('webinars_header'),
        FieldPanel('faq_header'),
        FieldPanel('faqs'),
        FieldPanel('demo_cta_text'),
        FieldPanel('demo_cta_link'),
        FieldPanel('tutor_login_link')
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
    parent_page_types = ['pages.HomePage', 'pages.RootPage']


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

    parent_page_type = ['pages.HomePage']
    template = 'page.html'
    max_count = 1
