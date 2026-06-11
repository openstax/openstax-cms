from django.db import models
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail_ai.panels import AIMultipleChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.api import APIField

from openstax.preview import FrontendPreviewMixin

from salesforce.models import School

from pages.custom_blocks import APIImageChooserBlock, \
    APIRichTextBlock, \
    LinkInfoBlock, \
    TEXT_ALIGNMENT_CHOICES, \
    hex_color_block, \
    gradient_config_options, \
    gradient_block_counts, \
    id_config_block


from .constants import BODY_BLOCKS


class RootPage(FrontendPreviewMixin, Page):
    layout = StreamField([
        ('default', blocks.StructBlock([
        ])),
        ('landing', blocks.StructBlock([
            ('nav_links', blocks.ListBlock(LinkInfoBlock(required=False, label="Link"),
                default=[],
                label='Nav Links'
            )),
            ('show_give_now_button', blocks.BooleanBlock(required=False, label="Show Give Button in Header", default=True)),
        ], label='Landing Page')),
    ], max_num=1, blank=True, collapsed=True, use_json_field=True, default=[])

    body = StreamField(BODY_BLOCKS + [
        ('tabbed_content', blocks.StructBlock([
            ('tabs', blocks.ListBlock(blocks.StructBlock([
                ('label', blocks.CharBlock(required=True, help_text='The visible label for this tab.')),
                ('content', blocks.StreamBlock(BODY_BLOCKS)),
            ]), label='Tabs')),
            ('config', blocks.StreamBlock([
                ('tab_alignment', blocks.ChoiceBlock(choices=TEXT_ALIGNMENT_CHOICES, help_text='Alignment of the tab labels. Default left.')),
                ('active_color', hex_color_block('Color of the active tab indicator. Must be hex eg: #ff0000.')),
                ('background_color', hex_color_block('Background color of the tabbed content area. Must be hex eg: #ff0000.')),
            ] + gradient_config_options() + [
                ('default_tab', blocks.IntegerBlock(min_value=0, help_text='Index of the default active tab (0-based). default 0.')),
                ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this block.')),
                ('border_width', blocks.IntegerBlock(min_value=0, help_text='Border width for the tab bar in pixels. default 0.')),
                ('id', id_config_block()),
            ], block_counts={
                'tab_alignment': {'max_num': 1},
                'active_color': {'max_num': 1},
                'background_color': {'max_num': 1},
                **gradient_block_counts(),
                'default_tab': {'max_num': 1},
                'analytics_label': {'max_num': 1},
                'border_width': {'max_num': 1},
                'id': {'max_num': 1},
            }, required=False)),
        ], label="Tabbed Content")),
    ], use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    school = models.ForeignKey(
        School,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Link a school to this landing page. School information will be included in the API response.'
    )

    def get_school_data(self):
        """Return serialized school data for API"""
        if self.school:
            from salesforce.serializers import SchoolSerializer
            serializer = SchoolSerializer(self.school)
            return serializer.data
        return None

    @cached_property
    def school_data(self):
        return self.get_school_data()

    api_fields = [
        APIField('layout'),
        APIField('body'),
        APIField('school_data'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    content_panels = [
        TitleFieldPanel('title', help_text="For CMS use only. Use 'Promote' tab above to edit SEO information."),
        FieldPanel('layout'),
        AutocompletePanel('school'),
        FieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'
    max_count = 1
    parent_page_types = ['wagtailcore.Page']

    def __str__(self):
        return self.path

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to / for the root page
        site_id, site_root_url, page_url_relative_to_site_root = url_parts

        return site_id, site_root_url, ''

    # serve_preview is provided by FrontendPreviewMixin.

# subclass of RootPage with a few overrides for subpages
class FlexPageRelatedPage(Orderable):
    page = ParentalKey('pages.FlexPage', related_name='related_pages', on_delete=models.CASCADE)
    related_page = models.ForeignKey('wagtailcore.Page', on_delete=models.CASCADE, related_name='+')


class FlexPage(RootPage):
    parent_page_types = ['pages.RootPage', 'pages.FlexPage']
    subpage_types = ['pages.FlexPage']
    template = 'page.html'
    max_count = None

    content_panels = RootPage.content_panels + [
        AIMultipleChooserPanel(
            'related_pages',
            chooser_field_name='related_page',
            vector_index='PageVectorIndex',
            label='Related pages',
        ),
    ]

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/{}'.format(self.slug)


#TODO: start removing these pages as we move to the above structure for all pages.

class HomePage(FrontendPreviewMixin, Page):
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
        ], max_num=4), use_json_field=True
    )
    features_tab1_explore_text = models.CharField(default='', blank=True, max_length=255)
    features_tab1_explore_url = models.URLField(blank=True, default='')
    features_tab1_explore_logged_in_text = models.CharField(default='', blank=True, max_length=255)
    features_tab1_explore_logged_in_url = models.URLField(blank=True, default='')
    features_tab2_features = StreamField(
        blocks.StreamBlock([
            ('feature_text', blocks.CharBlock())
        ], max_num=4), use_json_field=True
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

    k12_cta_header = models.CharField(max_length=255, blank=True, null=True)
    k12_cta_description = models.TextField(blank=True, null=True)
    k12_cta_link = models.URLField(blank=True, null=True)
    k12_cta_button_text = models.CharField(max_length=255, blank=True, null=True)
    research_cta_header = models.CharField(max_length=255, blank=True, null=True)
    research_cta_description = models.TextField(blank=True, null=True)
    research_cta_link = models.URLField(blank=True, null=True)
    research_cta_button_text = models.CharField(max_length=255, blank=True, null=True)
    quotes_headline = models.CharField(default='', blank=True, max_length=255)
    quotes = StreamField(
        blocks.StreamBlock([
            ('quote', blocks.ListBlock(blocks.StructBlock([
                ('testimonial', blocks.TextBlock(required=False)),
                ('author', blocks.CharBlock(Required=False)),
            ])))], max_num=2), use_json_field=True)
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
            ])))], max_num=4), use_json_field=True)
    whats_openstax_headline = models.CharField(default='', blank=True, max_length=255)
    whats_openstax_description = models.TextField(default='', blank=True)
    whats_openstax_interest_headline = models.CharField(default='', blank=True, max_length=255)
    whats_openstax_interest_text = models.TextField(default='', blank=True)
    whats_openstax_interest_link_text = models.CharField(default='', blank=True, max_length=255)
    whats_openstax_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    map_text = models.TextField(default='', blank=True)
    map_button_text = models.CharField(default='', blank=True, max_length=255)
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
        APIField('k12_cta_header'),
        APIField('k12_cta_description'),
        APIField('k12_cta_link'),
        APIField('k12_cta_button_text'),
        APIField('research_cta_header'),
        APIField('research_cta_description'),
        APIField('research_cta_link'),
        APIField('research_cta_button_text'),
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
        APIField('whats_openstax_interest_headline'),
        APIField('whats_openstax_interest_text'),
        APIField('whats_openstax_interest_link_text'),
        APIField('whats_openstax_image'),
        APIField('map_text'),
        APIField('map_button_text'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    max_count = 1

    class Meta:
        verbose_name = "Home Page"

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('banner_headline'),
        FieldPanel('banner_description'),
        FieldPanel('banner_get_started_text'),
        FieldPanel('banner_get_started_link'),
        FieldPanel('banner_login_text'),
        FieldPanel('banner_login_link'),
        FieldPanel('banner_logged_in_text'),
        FieldPanel('banner_logged_in_link'),
        FieldPanel('banner_left_image'),
        FieldPanel('banner_right_image'),
        FieldPanel('features_headline'),
        FieldPanel('features_tab1_heading'),
        FieldPanel('features_tab2_heading'),
        FieldPanel('features_tab1_features'),
        FieldPanel('features_tab1_explore_text'),
        FieldPanel('features_tab1_explore_url'),
        FieldPanel('features_tab1_explore_logged_in_text'),
        FieldPanel('features_tab1_explore_logged_in_url'),
        FieldPanel('features_tab2_features'),
        FieldPanel('features_tab2_explore_text'),
        FieldPanel('features_tab2_explore_url'),
        FieldPanel('features_bg_image'),
        FieldPanel('k12_cta_header'),
        FieldPanel('k12_cta_description'),
        FieldPanel('k12_cta_link'),
        FieldPanel('k12_cta_button_text'),
        FieldPanel('research_cta_header'),
        FieldPanel('research_cta_description'),
        FieldPanel('research_cta_link'),
        FieldPanel('research_cta_button_text'),
        FieldPanel('quotes_headline'),
        FieldPanel('quotes'),
        FieldPanel('quotes_instructor_image'),
        FieldPanel('quotes_student_image'),
        FieldPanel('tutor_logo'),
        FieldPanel('tutor_description'),
        FieldPanel('tutor_button_text'),
        FieldPanel('tutor_button_link'),
        FieldPanel('tutor_demo_text'),
        FieldPanel('tutor_demo_link'),
        FieldPanel('tutor_features'),
        FieldPanel('whats_openstax_headline'),
        FieldPanel('whats_openstax_description'),
        FieldPanel('whats_openstax_interest_headline'),
        FieldPanel('whats_openstax_interest_text'),
        FieldPanel('whats_openstax_interest_link_text'),
        FieldPanel('whats_openstax_image'),
        FieldPanel('map_text'),
        FieldPanel('map_button_text'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    # we are controlling what types of pages are allowed under a homepage
    # if a new page type is created, it needs to be added here to show up in
    # the admin
    subpage_types = [
        'pages.ContactUs',
        'pages.AboutUsPage',
        'pages.TeamPage',
        'pages.GeneralPage',
        'pages.Supporters',
        'pages.MapPage',
        'pages.Give',
        'pages.TermsOfService',
        'pages.FAQ',
        'pages.GiveForm',
        'pages.Accessibility',
        'pages.Licensing',
        'pages.Technology',
        'pages.ErrataList',
        'pages.PrivacyPolicy',
        'pages.PrintOrder',
        'pages.LearningResearchPage',
        'pages.Careers',
        'pages.Impact',
        'pages.InstitutionalPartnership',
        'pages.InstitutionalPartnerProgramPage',
        'pages.CreatorFestPage',
        'pages.PartnersPage',
        'pages.WebinarPage',
        'pages.MathQuizPage',
        'pages.LLPHPage',
        'pages.TutorMarketing',
        'pages.Subjects',
        'pages.FormHeadings',
        'pages.K12MainPage',
        'pages.K12Subject',
        'pages.AllyLogos',
        'pages.Assignable',
        'books.BookIndex',
        'news.NewsIndex',
        'news.PressIndex',
        'pages.RootPage',
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
        return site_id, root_url, '/'


class GeneralPage(FrontendPreviewMixin, Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('tagline', blocks.CharBlock(classname="full title")),
        ('paragraph', APIRichTextBlock()),
        ('image', APIImageChooserBlock()),
        ('html', blocks.RawHTMLBlock()),
    ], use_json_field=True)

    def get_sitemap_urls(self, *args, **kwargs):
        if self.slug not in ['kinetic', 'write-for-us', 'editorial-calendar']:
            return []

        return super().get_sitemap_urls(*args, **kwargs)

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the parents, all general pages are /{slug}
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/{}'.format(self.slug)

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
        TitleFieldPanel('title'),
        FieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]


