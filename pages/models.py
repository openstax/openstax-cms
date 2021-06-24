from django import forms
from django.db import models
from django.http.response import JsonResponse

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.api import APIField
from wagtail.core.models import Site

from openstax.functions import build_image_url, build_document_url
from books.models import Book
from webinars.models import Webinar
from news.models import BlogStreamBlock # for use on the ImpactStories

from salesforce.models import PartnerTypeMapping, PartnerFieldNameMapping, PartnerCategoryMapping, Partner

from .custom_blocks import ImageBlock, \
    APIImageChooserBlock, \
    ColumnBlock, \
    FAQBlock, \
    BookProviderBlock, \
    CardBlock, \
    CardImageBlock, \
    StoryBlock
from .custom_fields import Funder, \
    Institutions, \
    Group


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


class OpenStaxPeople(Orderable, Group):
    marketing_video = ParentalKey('pages.TeamPage', related_name='openstax_people')


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
    banner_headline = models.CharField(default='', blank=True, max_length=255)
    banner_description = models.TextField(default='', blank=True)
    banner_get_started_text = models.CharField(default='', blank=True, max_length=255)
    banner_get_started_link = models.URLField(blank=True, default='')
    banner_login_text = models.CharField(default='', blank=True, max_length=255)
    banner_login_link = models.URLField(blank=True, default='')
    banner_logged_in_text = models.CharField(default='', blank=True, max_length=255)
    banner_logged_in_link = models.URLField(blank=True, default='')
    banner_left_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    banner_right_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    features_headline = models.CharField(default='', blank=True, max_length=255)
    features_tab1_heading = models.CharField(default='', blank=True, max_length=255)
    features_tab2_heading = models.CharField(default='', blank=True, max_length=255)
    features_tab1_features = StreamField(
        blocks.StreamBlock([
            ('feature_text', blocks.CharBlock())
        ], max_num=4)
    )
    features_tab1_explore_text = models.CharField(default='', blank=True, max_length=255)
    features_tab1_explore_url = models.URLField(blank=True, default='')
    features_tab1_explore_logged_in_text = models.CharField(default='', blank=True, max_length=255)
    features_tab1_explore_logged_in_url = models.URLField(blank=True, default='')
    features_tab2_features = StreamField(
        blocks.StreamBlock([
            ('feature_text', blocks.CharBlock())
        ], max_num=4)
    )
    features_tab2_explore_text = models.CharField(default='', blank=True, max_length=255)
    features_tab2_explore_url = models.URLField(blank=True, default='')
    features_bg_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    quotes_headline = models.CharField(default='', blank=True, max_length=255)
    quotes = StreamField(
        blocks.StreamBlock([
            ('quote', blocks.ListBlock(blocks.StructBlock([
                ('testimonial', blocks.TextBlock(required=False)),
                ('author', blocks.CharBlock(Required=False)),
            ])))], max_num=2))
    quotes_instructor_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    quotes_student_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    tutor_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tutor_description = models.TextField(default='', blank=True)
    tutor_button_text = models.CharField(default='', blank=True, max_length=255)
    tutor_button_link = models.URLField(blank=True, default='')
    tutor_demo_text = models.CharField(default='', blank=True, max_length=255)
    tutor_demo_link = models.URLField(blank=True, default='')
    tutor_features = StreamField(
        blocks.StreamBlock([
            ('features', blocks.ListBlock(blocks.StructBlock([
                ('image', APIImageChooserBlock(required=False)),
                ('title', blocks.CharBlock(required=False)),
            ])))], max_num=4))
    whats_openstax_headline = models.CharField(default='', blank=True, max_length=255)
    whats_openstax_description = models.TextField(default='', blank=True)
    whats_openstax_donate_text = models.TextField(default='', blank=True)
    whats_openstax_give_text = models.CharField(default='', blank=True, max_length=255)
    whats_openstax_give_link = models.URLField(blank=True, default='')
    whats_openstax_learn_more_text = models.CharField(default='', blank=True, max_length=255)
    whats_openstax_learn_more_link = models.URLField(blank=True, default='')
    whats_openstax_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('banner_headline'),
        APIField('banner_description'),
        APIField('banner_get_started_text'),
        APIField('banner_get_started_link'),
        APIField('banner_login_text'),
        APIField('banner_login_link'),
        APIField('banner_logged_in_text'),
        APIField('banner_logged_in_link'),
        APIField('banner_left_image'),
        APIField('banner_right_image'),
        APIField('features_headline'),
        APIField('features_tab1_heading'),
        APIField('features_tab2_heading'),
        APIField('features_tab1_features'),
        APIField('features_tab1_explore_text'),
        APIField('features_tab1_explore_url'),
        APIField('features_tab1_explore_logged_in_text'),
        APIField('features_tab1_explore_logged_in_url'),
        APIField('features_tab2_features'),
        APIField('features_tab2_explore_text'),
        APIField('features_tab2_explore_url'),
        APIField('features_bg_image'),
        APIField('quotes_headline'),
        APIField('quotes'),
        APIField('quotes_instructor_image'),
        APIField('quotes_student_image'),
        APIField('tutor_logo'),
        APIField('tutor_description'),
        APIField('tutor_button_text'),
        APIField('tutor_button_link'),
        APIField('tutor_demo_text'),
        APIField('tutor_demo_link'),
        APIField('tutor_features'),
        APIField('whats_openstax_headline'),
        APIField('whats_openstax_description'),
        APIField('whats_openstax_donate_text'),
        APIField('whats_openstax_give_text'),
        APIField('whats_openstax_give_link'),
        APIField('whats_openstax_learn_more_text'),
        APIField('whats_openstax_learn_more_link'),
        APIField('whats_openstax_image'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    max_count = 1

    class Meta:
        verbose_name = "Home Page"


    content_panels = [
        FieldPanel('banner_headline'),
        FieldPanel('banner_description'),
        FieldPanel('banner_get_started_text'),
        FieldPanel('banner_get_started_link'),
        FieldPanel('banner_login_text'),
        FieldPanel('banner_login_link'),
        FieldPanel('banner_logged_in_text'),
        FieldPanel('banner_logged_in_link'),
        ImageChooserPanel('banner_left_image'),
        ImageChooserPanel('banner_right_image'),
        FieldPanel('features_headline'),
        FieldPanel('features_tab1_heading'),
        FieldPanel('features_tab2_heading'),
        StreamFieldPanel('features_tab1_features'),
        FieldPanel('features_tab1_explore_text'),
        FieldPanel('features_tab1_explore_url'),
        FieldPanel('features_tab1_explore_logged_in_text'),
        FieldPanel('features_tab1_explore_logged_in_url'),
        StreamFieldPanel('features_tab2_features'),
        FieldPanel('features_tab2_explore_text'),
        FieldPanel('features_tab2_explore_url'),
        ImageChooserPanel('features_bg_image'),
        FieldPanel('quotes_headline'),
        StreamFieldPanel('quotes'),
        ImageChooserPanel('quotes_instructor_image'),
        ImageChooserPanel('quotes_student_image'),
        ImageChooserPanel('tutor_logo'),
        FieldPanel('tutor_description'),
        FieldPanel('tutor_button_text'),
        FieldPanel('tutor_button_link'),
        FieldPanel('tutor_demo_text'),
        FieldPanel('tutor_demo_link'),
        StreamFieldPanel('tutor_features'),
        FieldPanel('whats_openstax_headline'),
        FieldPanel('whats_openstax_description'),
        FieldPanel('whats_openstax_donate_text'),
        FieldPanel('whats_openstax_give_text'),
        FieldPanel('whats_openstax_give_link'),
        FieldPanel('whats_openstax_learn_more_text'),
        FieldPanel('whats_openstax_learn_more_link'),
        ImageChooserPanel('whats_openstax_image'),
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
        'pages.Technology',
        'pages.ErrataList',
        'pages.PrivacyPolicy',
        'pages.PrintOrder',
        'pages.ResearchPage',
        'pages.Careers',
        'pages.Impact',
        'pages.InstitutionalPartnership',
        'pages.HeroJourneyPage',
        'pages.InstitutionalPartnerProgramPage',
        'pages.CreatorFestPage',
        'pages.PartnersPage',
        'pages.WebinarPage',
        'pages.MathQuizPage',
        'pages.LLPHPage',
        'pages.TutorMarketing',
        'pages.TutorLanding',
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
        ('html', blocks.RawHTMLBlock()),
    ])

    def get_sitemap_urls(self, request=None):
        return [
            {
                'location': '{}/general/{}'.format(Site.find_for_request(request).root_url, self.slug),
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]

    def get_url_parts(self, *args, **kwargs):
        url_parts = super(GeneralPage, self).get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, root_url, page_path = url_parts
        page_path = '/general' + page_path

        return (site_id, root_url, page_path)

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


class FoundationSupportFunders(Orderable, Funder):
    page = ParentalKey('pages.FoundationSupport', related_name='funders')


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

    def get_sitemap_urls(self, request=None):
        return []


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
        FieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('featured_provider_intro_blurb'),
        StreamFieldPanel('featured_providers'),
        FieldPanel('other_providers_intro_blurb'),
        StreamFieldPanel('providers'),
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


class ImpactStory(Page):
    date = models.DateField("Post date")
    heading = models.CharField(max_length=250, help_text="Heading displayed on website")
    subheading = models.CharField(max_length=250, blank=True, null=True)
    author = models.CharField(max_length=250)
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    featured_image_alt_text = models.CharField(max_length=250, blank=True, null=True)
    body = StreamField(BlogStreamBlock())

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        ImageChooserPanel('featured_image'),
        FieldPanel('featured_image_alt_text'),
        StreamFieldPanel('body'),
    ]

    api_fields = [
        APIField('date'),
        APIField('title'),
        APIField('heading'),
        APIField('subheading'),
        APIField('author'),
        APIField('featured_image'),
        APIField('featured_image_alt_text'),
        APIField('body'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_types = ['pages.Impact']


class Impact(Page):
    improving_access = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('image', ImageBlock()),
            ('heading', blocks.CharBlock()),
            ('description', blocks.RichTextBlock()),
            ('button_text', blocks.CharBlock()),
            ('button_href', blocks.URLBlock())
         ]))], max_num=1))
    reach = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('image', ImageBlock()),
            ('heading', blocks.CharBlock()),
            ('description', blocks.RichTextBlock()),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('icon', APIImageChooserBlock(required=False)),
                ('description', blocks.CharBlock()),
                ('link_text', blocks.CharBlock(required=False)),
                ('link_href', blocks.URLBlock(required=False))
            ])))
        ]))], max_num=1))
    quote = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('image', ImageBlock()),
            ('quote', blocks.RichTextBlock())
        ]))], max_num=1))
    making_a_difference = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('description', blocks.RichTextBlock()),
            ('stories', blocks.ListBlock(StoryBlock()))
        ]))], max_num=1))
    disruption = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('description', blocks.TextBlock()),
            ('graph', blocks.StructBlock([
                ('image', ImageBlock(required=False)),
                ('image_alt_text', blocks.CharBlock(required=False)),
            ]))
        ]))], max_num=1))
    supporter_community = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('image', ImageBlock()),
            ('quote', blocks.RichTextBlock()),
            ('link_text', blocks.CharBlock()),
            ('link_href', blocks.URLBlock())
        ]))], max_num=1))
    giving = StreamField(
        blocks.StreamBlock([
        ('content', blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('description', blocks.TextBlock()),
            ('link_text', blocks.CharBlock()),
            ('link_href', blocks.URLBlock()),
            ('nonprofit_statement', blocks.TextBlock()),
            ('annual_report_link_text', blocks.CharBlock()),
            ('annual_report_link_href', blocks.URLBlock()),
        ]))], max_num=1))

    content_panels = [
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        StreamFieldPanel('improving_access'),
        StreamFieldPanel('reach'),
        StreamFieldPanel('quote'),
        StreamFieldPanel('making_a_difference'),
        StreamFieldPanel('disruption'),
        StreamFieldPanel('supporter_community'),
        StreamFieldPanel('giving'),
    ]

    api_fields = [
        APIField('title'),
        APIField('improving_access'),
        APIField('reach'),
        APIField('quote'),
        APIField('making_a_difference'),
        APIField('disruption'),
        APIField('supporter_community'),
        APIField('giving'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    subpage_types = ['pages.ImpactStory']
    max_count = 1


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
        field_name_mappings = PartnerFieldNameMapping.objects.values_list('salesforce_name', flat=True).filter(hidden=False)
        field_name_mappings = list(field_name_mappings)

        for field in field_mappings:
            if any(name.startswith(field.salesforce_name) for name in field_name_mappings):
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


class LLPHPage(Page):
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
        FieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        ImageChooserPanel('hero_background'),
        FieldPanel('signup_link_href'),
        FieldPanel('signup_link_text'),
        DocumentChooserPanel('book_cover'),
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
        APIField('book_description'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']

    class Meta:
        verbose_name = "LLPH Page"


class TutorMarketing(Page):
    # header section
    header = models.CharField(max_length=255)
    description = models.TextField()
    header_cta_button_text = models.CharField(max_length=255)
    header_cta_button_link = models.URLField()
    quote = RichTextField()

    #features
    features_header = models.CharField(max_length=255)
    features_cards = StreamField([
        ('cards', CardImageBlock()),
    ])

    #availble books
    available_books_header = models.CharField(max_length=255)

    #cost
    cost_header = models.CharField(max_length=255)
    cost_description = models.TextField()
    cost_cards = StreamField([
        ('cards', CardBlock()),
    ])
    cost_institution_message = models.CharField(max_length=255)

    #feedback
    feedback_media = StreamField(
        blocks.StreamBlock([
            ('image', ImageBlock()),
            ('video', blocks.RawHTMLBlock())
        ], max_num=1))
    feedback_heading = models.CharField(max_length=255)
    feedback_quote = models.TextField()
    feedback_name = models.CharField(max_length=255)
    feedback_occupation = models.CharField(max_length=255)
    feedback_organization = models.CharField(max_length=255)

    #webinars
    webinars_header = models.CharField(max_length=255)

    #faq
    faq_header = models.CharField(max_length=255)
    faqs = StreamField([
        ('faq', FAQBlock()),
    ])

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
        APIField('quote'),
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
        FieldPanel('title', classname="full title"),
        FieldPanel('header'),
        FieldPanel('description'),
        FieldPanel('header_cta_button_text'),
        FieldPanel('header_cta_button_link'),
        FieldPanel('quote'),
        FieldPanel('features_header'),
        StreamFieldPanel('features_cards'),
        FieldPanel('available_books_header'),
        FieldPanel('cost_header'),
        FieldPanel('cost_description'),
        StreamFieldPanel('cost_cards'),
        FieldPanel('cost_institution_message'),
        StreamFieldPanel('feedback_media'),
        FieldPanel('feedback_heading'),
        FieldPanel('feedback_quote'),
        FieldPanel('feedback_name'),
        FieldPanel('feedback_occupation'),
        FieldPanel('feedback_organization'),
        FieldPanel('webinars_header'),
        FieldPanel('faq_header'),
        StreamFieldPanel('faqs'),
        FieldPanel('demo_cta_text'),
        FieldPanel('demo_cta_link'),
        FieldPanel('tutor_login_link')
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


class TutorLanding(Page):
    # header section
    header = models.CharField(max_length=255)
    description = models.TextField()
    available_books_header = models.CharField(max_length=255)
    case_study_cta = models.CharField(max_length=255)
    case_study_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_case_study_file(self):
        return build_document_url(self.case_study_file.url)
    case_study_file_url = property(get_case_study_file)

    #features
    features_header = models.CharField(max_length=255)
    features_cards = StreamField([
        ('cards', CardImageBlock()),
    ])

    #other resource
    other_resources_text = models.TextField()
    other_resources_cta = models.CharField(max_length=255)
    other_resources_link = models.URLField()

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
            book_data.append({
                'id': book.id,
                'slug': 'books/{}'.format(book.slug),
                'title': book.title,
                'cover_url': book.cover_url,
            })
        return book_data

    api_fields = [
        APIField('title'),
        APIField('header'),
        APIField('description'),
        APIField('available_books_header'),
        APIField('tutor_books'),
        APIField('case_study_cta'),
        APIField('case_study_file_url'),
        APIField('features_header'),
        APIField('features_cards'),
        APIField('other_resources_text'),
        APIField('other_resources_cta'),
        APIField('other_resources_link'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('header'),
        FieldPanel('description'),
        FieldPanel('available_books_header'),
        FieldPanel('case_study_cta'),
        DocumentChooserPanel('case_study_file'),
        FieldPanel('features_header'),
        StreamFieldPanel('features_cards'),
        FieldPanel('other_resources_text'),
        FieldPanel('other_resources_cta'),
        FieldPanel('other_resources_link'),
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
