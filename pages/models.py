from django import forms
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.api import APIField
from wagtail.models import Site

from api.models import FeatureFlag
from openstax.functions import build_image_url, build_document_url
from books.models import Book, SubjectBooks, BookFacultyResources, BookStudentResources
from webinars.models import Webinar
from news.models import BlogStreamBlock  # for use on the ImpactStories

from salesforce.models import PartnerTypeMapping, PartnerFieldNameMapping, PartnerCategoryMapping, Partner

from .custom_blocks import ImageBlock, \
    APIImageChooserBlock, \
    FAQBlock, \
    BookProviderBlock, \
    CardBlock, \
    CardImageBlock, \
    StoryBlock, \
    TutorAdBlock, \
    AboutOpenStaxBlock, \
    InfoBoxBlock, \
    TestimonialBlock, \
    AllyLogoBlock, \
    AssignableBookBlock, \
    DividerBlock, \
    APIRichTextBlock, \
    CTAButtonBarBlock, \
    LinksGroupBlock, \
    QuoteBlock, \
    LinkInfoBlock, \
    CTALinkBlock

from .custom_fields import Group
import snippets.models as snippets

# Constants for styling options on Root/Flex pages
# consider moving to a constants.py file
CARDS_STYLE_CHOICES = [
    ('rounded', 'Rounded'),
    ('square', 'Square'),
]
HERO_IMAGE_ALIGNMENT_CHOICES = [
    ('left', 'Left'),
    ('right', 'Right'),
    ('top_left', 'Top Left'),
    ('top_right', 'Top Right'),
    ('bottom_left', 'Bottom Left'),
    ('bottom_right', 'Bottom Right'),
]
SECTION_CONTENT_BLOCKS = [
    ('cards_block', blocks.StructBlock([
        ('cards', blocks.ListBlock(
            blocks.StructBlock([
                ('text', APIRichTextBlock()),
                ('cta_block', blocks.ListBlock(CTALinkBlock(required=False, label="Link"),
                    default=[],
                    max_num=1,
                    label='Call To Action'
                )),
            ]),
        )),
        ('config', blocks.StreamBlock([
            ('card_size', blocks.IntegerBlock(min_value=0, help_text='Sets the width of the individual cards. default 27.')),
            ('card_style', blocks.ChoiceBlock(choices=CARDS_STYLE_CHOICES, help_text='The border style of the cards. default borderless.')),
        ], block_counts={
            'card_size': {'max_num': 1},
            'card_style': {'max_num': 1},
        }, required=False)),
    ], label="Cards Block")),
    ('text', APIRichTextBlock()),
    ('html', blocks.RawHTMLBlock()),
    ('cta_block', CTAButtonBarBlock()),
    ('links_group', LinksGroupBlock()),
    ('quote', QuoteBlock()),
    ('faq', blocks.StreamBlock([
        ('faq', FAQBlock()),
    ]))
]

# we have one RootPage, which is the parent of all other pages
# this is the only page that should be created at the top level of the page tree
# this should be the homepage
class RootPage(Page):
    layout = StreamField([
        ('default', blocks.StructBlock([
        ])),
        ('landing', blocks.StructBlock([
            ('nav_links', blocks.ListBlock(LinkInfoBlock(required=False, label="Link"),
                default=[],
                label='Nav Links'
            )),
        ], label='Landing Page')),
    ], max_num=1, blank=True, collapsed=True, use_json_field=True, default=[])

    body = StreamField([
        ('hero', blocks.StructBlock([
            ('content', blocks.StreamBlock(SECTION_CONTENT_BLOCKS)),
            ('image', APIImageChooserBlock(required=False)),
            ('image_alt', blocks.CharBlock(required=False)),
            ('config', blocks.StreamBlock([
                ('image_alignment', blocks.ChoiceBlock(choices=HERO_IMAGE_ALIGNMENT_CHOICES, help_text='Controls if the image is on the left or right side of the content, and if it prefers to be at the top, center, or bottom of the available space.')),
                ('id', blocks.RegexBlock(
                    regex=r'[a-zA-Z0-9\-_]',
                    help_text='HTML id of this element. not visible to users, but is visible in urls and is used to link to a certain part of the page with an anchor link. eg: cool_section',
                    error_mssages={'invalid': 'not a valid id.'}
                )),
                ('background_color', blocks.RegexBlock(
                    regex=r'#[a-zA-Z0-9]{6}',
                    help_text='Sets the background color of the section. value must be hex eg: #ff0000. Default grey.',
                    error_mssages={'invalid': 'not a valid hex color.'}
                )),
                ('padding', blocks.IntegerBlock(min_value=0, help_text='Creates space above and below this section. default 0.')),
                ('padding_top', blocks.IntegerBlock(min_value=0, help_text='Creates space above this section. default 0.')),
                ('padding_bottom', blocks.IntegerBlock(min_value=0, help_text='Creates space below this section. default 0.')),
                ('text_alignment', blocks.ChoiceBlock(choices=[
                    ('center', 'Center'),
                    ('left', 'Left'),
                    ('right', 'Right'),
                ], default='left', help_text='Configures text alignment within the container. Default Left.')),
                ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this section.')),
            ], block_counts={
                'image_alignment': {'max_num': 1},
                'id': {'max_num': 1},
                'background_color': {'max_num': 1},
                'padding': {'max_num': 1},
                'padding_top': {'max_num': 1},
                'padding_bottom': {'max_num': 1},
                'text_alignment': {'max_num': 1},
                'analytics_label': {'max_num': 1},
            }, required=False))
        ])),
        ('section', blocks.StructBlock([
            ('content', blocks.StreamBlock(SECTION_CONTENT_BLOCKS)),
            ('config', blocks.StreamBlock([
                ('id', blocks.RegexBlock(
                    regex=r'[a-zA-Z0-9\-_]',
                    help_text='HTML id of this element. not visible to users, but is visible in urls and is used to link to a certain part of the page with an anchor link. eg: cool_section',
                    error_mssages={'invalid': 'not a valid id.'}
                )),
                ('background_color', blocks.RegexBlock(
                    regex=r'#[a-zA-Z0-9]{6}',
                    help_text='Sets the background color of the section. value must be hex eg: #ff0000. Default grey.',
                    error_mssages={'invalid': 'not a valid hex color.'}
                )),
                ('padding', blocks.IntegerBlock(min_value=0, help_text='Creates space above and below this section. default 0.')),
                ('padding_top', blocks.IntegerBlock(min_value=0, help_text='Creates space above this section. default 0.')),
                ('padding_bottom', blocks.IntegerBlock(min_value=0, help_text='Creates space below this section. default 0.')),
                ('text_alignment', blocks.ChoiceBlock(choices=[
                    ('center', 'Center'),
                    ('left', 'Left'),
                    ('right', 'Right'),
                ], default='left', help_text='Configures text alignment within the container. Default Left.')),
                ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this section.')),
            ], block_counts={
                'id': {'max_num': 1},
                'background_color': {'max_num': 1},
                'padding': {'max_num': 1},
                'padding_top': {'max_num': 1},
                'padding_bottom': {'max_num': 1},
                'text_alignment': {'max_num': 1},
                'analytics_label': {'max_num': 1},
            }, required=False))
        ])),
        ('divider', DividerBlock()),
        ('html', blocks.RawHTMLBlock()),
    ], use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('layout'),
        APIField('body'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    content_panels = [
        TitleFieldPanel('title', help_text="For CMS use only. Use 'Promote' tab above to edit SEO information."),
        FieldPanel('layout'),
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
    # TODO: we are allowing this to be built as a child of the homepage. Not ideal.
    # Once the home page is released, use something to migrate homepage children to root page and remove this parent type.
    parent_page_types = ['wagtailcore.Page', 'pages.HomePage']
    subpage_types = ['pages.FlexPage']  # which might also require allowing all pages to be children.

    def __str__(self):
        return self.path

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to / for the root page
        site_id, site_root_url, page_url_relative_to_site_root = url_parts

        return site_id, site_root_url, ''

    def serve_preview(self, request, mode_name):
        site_id, site_root, relative_page_url = self.get_url_parts(request)
        preview_url = '{}{}/?preview={}'.format(site_root, relative_page_url, mode_name)

        return render(
            request,
            "preview.html",
            {"preview_url": preview_url},
        )

# subclass of RootPage with a few overrides for subpages
class FlexPage(RootPage):
    parent_page_types = ['pages.RootPage', 'pages.FlexPage']
    subpage_types = ['pages.FlexPage']
    template = 'page.html'
    max_count = None

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/{}'.format(self.slug)


#TODO: start removing these pages as we move to the above structure for all pages.

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
    ], use_json_field=True)
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
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('who_heading'),
        FieldPanel('who_paragraph'),
        FieldPanel('who_image'),
        FieldPanel('what_heading'),
        FieldPanel('what_paragraph'),
        FieldPanel('what_cards'),
        FieldPanel('where_heading'),
        FieldPanel('where_paragraph'),
        FieldPanel('where_map'),
        FieldPanel('where_map_alt'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')

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
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('header'),
        FieldPanel('subheader'),
        FieldPanel('header_image'),
        FieldPanel('team_header'),
        InlinePanel('openstax_people', label="OpenStax People"),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')

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


class K12MainPage(Page):
    banner_headline = models.CharField(default='', blank=True, max_length=255)
    banner_description = models.TextField(default='', blank=True)
    banner_right_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subject_list_default = models.CharField(default='Find Your Subject', blank=True, max_length=255)
    features_cards = StreamField([
        ('features_cards', CardImageBlock()),
    ], use_json_field=True)
    highlights_header = RichTextField(default='', blank=True)
    highlights = StreamField(
        blocks.StreamBlock([
            ('highlight', blocks.ListBlock(blocks.StructBlock([
                ('highlight_subheader', blocks.TextBlock(required=False)),
                ('highlight_text', blocks.CharBlock(Required=False)),
            ])))], max_num=3), use_json_field=True)
    highlights_icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    stats_grid = StreamField(
        blocks.StreamBlock([
            ('stat', blocks.ListBlock(blocks.StructBlock([
                ('bold_stat_text', blocks.TextBlock(required=False)),
                ('normal_stat_text', blocks.CharBlock(required=False)),
            ])))], max_num=3), use_json_field=True)
    stats_image1 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    stats_image2 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    stats_image3 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subject_library_header = models.CharField(default='', blank=True, max_length=255)
    subject_library_description = models.TextField(default='', blank=True)
    testimonials_header = models.CharField(default='', blank=True, max_length=255)
    testimonials_description = models.TextField(default='', blank=True)
    testimonials = StreamField([
        ('testimonials', TestimonialBlock()),
    ], use_json_field=True)
    faq_header = models.CharField(default='', blank=True, max_length=255)
    faqs = StreamField([
        ('faq', FAQBlock()),
    ], use_json_field=True)
    rfi_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    rfi_header = models.CharField(default='', blank=True, max_length=255)
    rfi_description = models.TextField(default='', blank=True)
    sticky_header = models.CharField(default='', blank=True, max_length=255)
    sticky_description = models.TextField(default='', blank=True)

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /k12
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return (site_id, site_root_url, '/k12')

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def k12library(self):
        subject_list = {}
        for subject in snippets.K12Subject.objects.filter(locale=self.locale).order_by('name'):
            subject_categories = {}
            subject_categories['color'] = subject.subject_color
            subject_categories['image'] = subject.subject_image
            subject_categories['link'] = subject.subject_link
            subject_categories['subject_category'] = subject.subject_category
            subject_list[subject.name] = subject_categories
        return subject_list

    api_fields = [
        APIField('title'),
        APIField('banner_headline'),
        APIField('banner_description'),
        APIField('banner_right_image'),
        APIField('subject_list_default'),
        APIField('features_cards'),
        APIField('highlights_header'),
        APIField('highlights'),
        APIField('highlights_icon'),
        APIField('stats_grid'),
        APIField('stats_image1'),
        APIField('stats_image2'),
        APIField('stats_image3'),
        APIField('subject_library_header'),
        APIField('subject_library_description'),
        APIField('k12library'),
        APIField('testimonials_header'),
        APIField('testimonials_description'),
        APIField('testimonials'),
        APIField('faq_header'),
        APIField('faqs'),
        APIField('rfi_image'),
        APIField('rfi_header'),
        APIField('rfi_description'),
        APIField('sticky_header'),
        APIField('sticky_description'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    class Meta:
        verbose_name = "K12 Main Page"

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('banner_headline'),
        FieldPanel('banner_description'),
        FieldPanel('banner_right_image'),
        FieldPanel('features_cards'),
        FieldPanel('highlights_header'),
        FieldPanel('highlights'),
        FieldPanel('highlights_icon'),
        FieldPanel('stats_grid'),
        FieldPanel('stats_image1'),
        FieldPanel('stats_image2'),
        FieldPanel('stats_image3'),
        FieldPanel('subject_library_header'),
        FieldPanel('subject_library_description'),
        FieldPanel('testimonials_header'),
        FieldPanel('testimonials_description'),
        FieldPanel('testimonials'),
        FieldPanel('faq_header'),
        FieldPanel('faqs'),
        FieldPanel('rfi_image'),
        FieldPanel('rfi_header'),
        FieldPanel('rfi_description'),
        FieldPanel('sticky_header'),
        FieldPanel('sticky_description')
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    max_count = 1
    template = 'page.html'
    parent_page_types = ['pages.HomePage']
    subpage_types = ['pages.K12Subject']


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


class Supporters(Page):
    banner_heading = models.CharField(default='', max_length=255)
    banner_description = models.TextField(default='')
    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    funder_groups = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('group_title', blocks.CharBlock(classname="name of funder group")),
                ('description', blocks.TextBlock(classname="description of funder group")),
                ('image', APIImageChooserBlock(required=False)),
                ('funders', blocks.ListBlock(blocks.StructBlock([
                    ('funder_name', blocks.CharBlock(required=True)),
                    ('url', blocks.URLBlock(required=False))

                ])))
            ]))]), use_json_field=True)

    disclaimer = models.TextField(default='')

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    api_fields = [
        APIField('title'),
        APIField('banner_heading'),
        APIField('banner_description'),
        APIField('banner_image'),
        APIField('funder_groups'),
        APIField('disclaimer'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('banner_heading'),
        FieldPanel('banner_description'),
        FieldPanel('banner_image'),
        FieldPanel('funder_groups'),
        FieldPanel('disclaimer')
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
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
    ], null=True, use_json_field=True)
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
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('header_text'),
        FieldPanel('map_image'),
        FieldPanel('section_1_cards'),
        FieldPanel('section_2_header_1'),
        FieldPanel('section_2_blurb_1'),
        FieldPanel('section_2_cta_1'),
        FieldPanel('section_2_link_1'),
        FieldPanel('section_2_image_1'),
        FieldPanel('section_2_header_2'),
        FieldPanel('section_2_blurb_2'),
        FieldPanel('section_2_cta_2'),
        FieldPanel('section_2_link_2'),
        FieldPanel('section_2_image_2'),
        FieldPanel('section_3_heading'),
        FieldPanel('section_3_blurb'),
        FieldPanel('section_3_cta'),
        FieldPanel('section_3_link'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
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
        TitleFieldPanel('title', classname='full title'),
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
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
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
    ], use_json_field=True)

    api_fields = [
        APIField('intro_heading'),
        APIField('intro_description'),
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

    api_fields = [
        APIField('title'),
        APIField('page_description'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('page_description'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
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
        TitleFieldPanel('title', classname="full title"),
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
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')

    ]

    template = 'page.html'
    parent_page_types = ['pages.HomePage']
    max_count = 1


class ErrataList(Page):
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
        APIField('correction_schedule'),
        APIField('deprecated_errata_message'),
        APIField('new_edition_errata_message'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
        APIField('about_header'),
        APIField('about_text'),
        APIField('about_popup')
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

    parent_page_types = ['pages.HomePage']
    max_count = 1


class PrintOrder(Page):
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

    parent_page_types = ['pages.HomePage']
    max_count = 1


class LearningResearchPage(Page):
    mission_body = models.TextField()
    banner_header = models.TextField(default='', blank=True)
    banner_body = models.TextField(default='', blank=True)
    bannerCTA = models.TextField(default='', blank=True)
    bannerURL = models.URLField(default='', blank=True)
    research_area_header = models.CharField(max_length=255)
    research_area_description_mobile = RichTextField(
        help_text="Research Area Description (Mobile Only)",
        default=""
    )
    research_areas_list = StreamField(
        blocks.StreamBlock([
            ('research_area_section', blocks.StructBlock([
                ('research_area_title', blocks.CharBlock()),
                ('research_area_blurb', blocks.RichTextBlock()),
                ('research_area_blurb_mobile', blocks.RichTextBlock()),
                ('research_areas', blocks.ListBlock(blocks.StructBlock([
                    ('header', blocks.CharBlock()),
                    ('description', blocks.CharBlock()),
                    ('short_description', blocks.CharBlock(
                        label="Short Description (Mobile Only)",
                        help_text="Short Description (Mobile Only)"
                    )),
                    ('photo', APIImageChooserBlock(required=False)),
                    ('cta_text', blocks.CharBlock(required=False)),
                    ('cta_link', blocks.URLBlock(required=False)),
                    ('publication', blocks.URLBlock(required=False)),
                    ('github', blocks.URLBlock(required=False)),
                ])))
            ]))]), default='', use_json_field=True)
    people_header = models.CharField(max_length=255)
    current_members = StreamField([
        ('person', blocks.StructBlock([
            ('first_name', blocks.CharBlock()),
            ('last_name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('long_title', blocks.CharBlock(required=False)),
            ('bio', blocks.CharBlock()),
            ('education', blocks.CharBlock(required=False)),
            ('specialization', blocks.CharBlock(required=False)),
            ('research_interest', blocks.CharBlock(required=False)),
            ('photo', APIImageChooserBlock(required=False)),
            ('website', blocks.URLBlock(required=False)),
            ('linked_in', blocks.URLBlock(required=False)),
            ('google_scholar', blocks.URLBlock(required=False)),
        ], icon='user')),
    ], null=True, blank=True, use_json_field=True)
    collaborating_researchers = StreamField([
        ('person', blocks.StructBlock([
            ('first_name', blocks.CharBlock()),
            ('last_name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('long_title', blocks.CharBlock(required=False)),
            ('bio', blocks.CharBlock()),
            ('education', blocks.CharBlock(required=False)),
            ('specialization', blocks.CharBlock(required=False)),
            ('research_interest', blocks.CharBlock(required=False)),
            ('photo', APIImageChooserBlock(required=False)),
            ('website', blocks.URLBlock(required=False)),
            ('linked_in', blocks.URLBlock(required=False)),
            ('google_scholar', blocks.URLBlock(required=False)),
        ], icon='user')),
    ], null=True, blank=True, use_json_field=True)
    alumni = StreamField([
        ('person', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('linked_in', blocks.URLBlock(required=False)),
        ], icon='user')),
    ], null=True, blank=True, use_json_field=True)
    publication_header = models.CharField(max_length=255)
    publications = StreamField([
        ('publication', blocks.StructBlock([
            ('authors', blocks.CharBlock()),
            ('date', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('excerpt', blocks.CharBlock()),
            ('pdf', blocks.URLBlock()),
            ('github', blocks.URLBlock(required=False)),
        ], icon='document')),
    ], null=True, blank=True, use_json_field=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('mission_body'),
        FieldPanel('banner_header'),
        FieldPanel('banner_body'),
        FieldPanel('bannerCTA'),
        FieldPanel('bannerURL'),
        FieldPanel('research_area_header'),
        FieldPanel('research_area_description_mobile'),
        FieldPanel('research_areas_list'),
        FieldPanel('people_header'),
        FieldPanel('current_members'),
        FieldPanel('collaborating_researchers'),
        FieldPanel('alumni'),
        FieldPanel('publication_header'),
        FieldPanel('publications'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    api_fields = [
        APIField('mission_body'),
        APIField('banner_header'),
        APIField('banner_body'),
        APIField('bannerCTA'),
        APIField('bannerURL'),
        APIField('research_area_header'),
        APIField('research_area_description_mobile'),
        APIField('research_areas_list'),
        APIField('people_header'),
        APIField('current_members'),
        APIField('collaborating_researchers'),
        APIField('alumni'),
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
        TitleFieldPanel('title', classname='full title'),
        FieldPanel('intro_heading'),
        FieldPanel('careers_content'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
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
    body = StreamField(BlogStreamBlock(), use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        TitleFieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        FieldPanel('featured_image'),
        FieldPanel('featured_image_alt_text'),
        FieldPanel('body'),
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
    template = 'page.html'

    def get_url_parts(self, *args, **kwargs):
        return None

    def get_sitemap_urls(self, request=None):
        return []


class Impact(Page):
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
            ]))], max_num=1), use_json_field=True)
    improving_access = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('image', ImageBlock()),
                ('heading', blocks.CharBlock()),
                ('description', blocks.RichTextBlock()),
                ('button_text', blocks.CharBlock()),
                ('button_href', blocks.URLBlock()),
                ('cards', blocks.ListBlock(blocks.StructBlock([
                    ('icon', APIImageChooserBlock(required=False)),
                    ('description', blocks.CharBlock()),
                    ('link_text', blocks.CharBlock(required=False)),
                    ('link_href', blocks.URLBlock(required=False))
                ])))
            ]))], max_num=1), use_json_field=True)
    quote = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('image', ImageBlock()),
                ('quote', blocks.RichTextBlock())
            ]))], max_num=1), use_json_field=True)
    making_a_difference = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('description', blocks.RichTextBlock()),
                ('stories', blocks.ListBlock(StoryBlock()))
            ]))], max_num=1), use_json_field=True)
    disruption = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('description', blocks.TextBlock()),
                ('graph', blocks.StructBlock([
                    ('image', ImageBlock(required=False)),
                    ('image_alt_text', blocks.CharBlock(required=False)),
                ]))
            ]))], max_num=1), use_json_field=True)
    supporter_community = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('image', ImageBlock()),
                ('quote', blocks.RichTextBlock()),
                ('link_text', blocks.CharBlock()),
                ('link_href', blocks.URLBlock())
            ]))], max_num=1), use_json_field=True)
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
            ]))], max_num=1), use_json_field=True)

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('improving_access'),
        FieldPanel('reach'),
        FieldPanel('quote'),
        FieldPanel('making_a_difference'),
        FieldPanel('disruption'),
        FieldPanel('supporter_community'),
        FieldPanel('giving'),
    ]

    api_fields = [
        APIField('title'),
        APIField('reach'),
        APIField('improving_access'),
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
    template = 'page.html'


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
    ], null=True, use_json_field=True)
    quote = models.TextField()
    quote_author = models.CharField(max_length=255)
    quote_title = models.CharField(max_length=255, blank=True, null=True)
    quote_school = models.CharField(max_length=255, blank=True, null=True)
    application_quote = models.TextField(blank=True, null=True)
    application_quote_author = models.CharField(max_length=255, blank=True, null=True)
    application_quote_title = models.CharField(max_length=255, blank=True, null=True)
    application_quote_school = models.CharField(max_length=255, blank=True, null=True)
    application_link = models.URLField(blank=True, null=True)

    content_panels = [
        TitleFieldPanel('title'),
        FieldPanel('heading_image'),
        FieldPanel('heading_year'),
        FieldPanel('heading'),
        FieldPanel('program_tab_content'),
        FieldPanel('quote'),
        FieldPanel('quote_author'),
        FieldPanel('quote_title'),
        FieldPanel('quote_school'),
        FieldPanel('application_quote'),
        FieldPanel('application_quote_author'),
        FieldPanel('application_quote_title'),
        FieldPanel('application_quote_school'),
        FieldPanel('application_link'),
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
        APIField('application_link'),
        APIField('title'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    template = 'page.html'
    max_count = 1


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
    ], use_json_field=True)
    section_3_tall_cards = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('html', blocks.RichTextBlock()),
            ('link', blocks.URLBlock()),
            ('link_text', blocks.CharBlock())
        ])))
    ], use_json_field=True)
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
    ], use_json_field=True)
    section_7_heading = models.CharField(max_length=255)
    section_7_subheading = models.CharField(max_length=255)
    section_7_icons = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('image', ImageBlock()),
            ('image_alt_text', blocks.CharBlock()),
            ('current_cohort', blocks.BooleanBlock(required=False))
        ])))
    ], use_json_field=True)
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
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('section_1_heading'),
        FieldPanel('section_1_description'),
        FieldPanel('section_1_link_text'),
        FieldPanel('section_1_link'),
        FieldPanel('section_1_background_image'),
        FieldPanel('quote'),
        FieldPanel('quote_name'),
        FieldPanel('quote_title'),
        FieldPanel('quote_school'),
        FieldPanel('section_2_heading'),
        FieldPanel('section_2_description'),
        FieldPanel('section_2_image'),
        FieldPanel('section_2_image_alt'),
        FieldPanel('section_3_heading'),
        FieldPanel('section_3_description'),
        FieldPanel('section_3_wide_cards'),
        FieldPanel('section_3_tall_cards'),
        FieldPanel('section_4_quote_text'),
        FieldPanel('section_4_quote_name'),
        FieldPanel('section_4_quote_title'),
        FieldPanel('section_4_quote_school'),
        FieldPanel('section_4_background_image'),
        FieldPanel('section_5_heading'),
        FieldPanel('section_5_description'),
        FieldPanel('section_5_image'),
        FieldPanel('section_5_image_alt'),
        FieldPanel('section_5_image_caption'),
        FieldPanel('section_6_heading'),
        FieldPanel('section_6_description'),
        FieldPanel('section_6_cards'),
        FieldPanel('section_7_heading'),
        FieldPanel('section_7_subheading'),
        FieldPanel('section_7_icons'),
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
    template = 'page.html'


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
            ('paragraph', blocks.RichTextBlock(required=False)),
            ('cards', blocks.ListBlock(blocks.StructBlock([
                ('icon', ImageBlock()),
                ('headline', blocks.CharBlock()),
                ('description', blocks.RichTextBlock())
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
    template = 'page.html'


class PartnersPage(Page):
    heading = models.CharField(max_length=255)
    description = RichTextField()
    partner_landing_page_link = models.CharField(max_length=255, null=True, blank=True,
                                                 help_text="Link text to partner landing page.")
    partner_request_info_link = models.CharField(max_length=255, null=True, blank=True,
                                                 help_text="Forstack form link text")
    partner_full_partner_heading = models.CharField(max_length=255, null=True, blank=True)
    partner_full_partner_description = models.TextField(null=True, blank=True)
    partner_ally_heading = models.CharField(max_length=255, null=True, blank=True)
    partner_ally_description = models.TextField(null=True, blank=True)

    @staticmethod
    def category_mapping():
        field_mappings = PartnerCategoryMapping.objects.all()
        mapping_dict = {}
        field_name_mappings = PartnerFieldNameMapping.objects.values_list('salesforce_name', flat=True).filter(
            hidden=False)
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
        partner_types_array = []
        partner_type_mappings = PartnerTypeMapping.objects.all()
        types_from_partners = Partner.objects.values_list('partner_type', flat=True).exclude(partner_type__isnull=True)
        for partner_type in partner_type_mappings:
            if any(p_type.lower().startswith(partner_type.display_name.lower()) for p_type in types_from_partners):
                partner_types_array.append(partner_type.display_name)

        return partner_types_array

    content_panels = [
        TitleFieldPanel('title', classname='full title', help_text="Internal name for page."),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('partner_landing_page_link'),
        FieldPanel('partner_request_info_link'),
        FieldPanel('partner_full_partner_heading'),
        FieldPanel('partner_full_partner_description'),
        FieldPanel('partner_ally_heading'),
        FieldPanel('partner_ally_description'),
    ]

    api_fields = [
        APIField('title'),
        APIField('heading'),
        APIField('description'),
        APIField('partner_landing_page_link'),
        APIField('partner_request_info_link'),
        APIField('partner_full_partner_heading'),
        APIField('partner_full_partner_description'),
        APIField('partner_ally_heading'),
        APIField('partner_ally_description'),
        APIField('category_mapping'),
        APIField('field_name_mapping'),
        APIField('partner_type_choices'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    template = 'page.html'


class WebinarPage(Page):
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
        APIField('book_description'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
    ]

    parent_page_type = ['pages.HomePage']
    template = 'page.html'

    class Meta:
        verbose_name = "LLPH Page"


class TutorMarketing(Page):
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

    parent_page_types = ['pages.HomePage']
    max_count = 1


class Subjects(Page):
    heading = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    heading_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tutor_ad = StreamField([
        ('content', TutorAdBlock()),
    ], use_json_field=True)

    about_os = StreamField([
        ('content', AboutOpenStaxBlock()),
    ], use_json_field=True)

    info_boxes = StreamField([
        ('info_box', blocks.ListBlock(InfoBoxBlock())),
    ], use_json_field=True)

    philanthropic_support = models.TextField(blank=True, null=True)
    translations = StreamField([
        ('translation', blocks.ListBlock(blocks.StructBlock([
            ('locale', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def subjects(self):
        subject_list = {}
        for subject in snippets.Subject.objects.filter(locale=self.locale).order_by('name'):
            subject_categories = {}
            categories = []
            subject_categories['icon'] = subject.subject_icon
            for category in snippets.SubjectCategory.objects.filter(subject_id=subject.id).order_by('subject_category'):
                categories.append(category.subject_category)
            subject_categories['categories'] = categories
            subject_list[subject.name] = subject_categories

        return subject_list

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /subjects
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/subjects'

    api_fields = [
        APIField('heading'),
        APIField('description'),
        APIField('heading_image'),
        APIField('tutor_ad'),
        APIField('about_os'),
        APIField('info_boxes'),
        APIField('philanthropic_support'),
        APIField('subjects'),
        APIField('translations'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('heading_image'),
        FieldPanel('tutor_ad'),
        FieldPanel('about_os'),
        FieldPanel('info_boxes'),
        FieldPanel('philanthropic_support'),
        FieldPanel('translations'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    subpage_types = ['pages.Subject']
    max_count = 1

    class Meta:
        verbose_name = "New Subjects Page"


class SubjectOrderable(Orderable, SubjectBooks):
    page = ParentalKey("pages.Subject", related_name="subject")

    panels = [
        FieldPanel("subject"),
    ]


class Subject(Page):
    page_description = models.TextField(default='')
    tutor_ad = StreamField([
        ('content', TutorAdBlock()),
    ], null=True, blank=True, use_json_field=True)

    blog_header = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('blog_description', blocks.TextBlock()),
                ('link_text', blocks.CharBlock()),
                ('link_href', blocks.URLBlock())
            ]))], max_num=1), use_json_field=True)

    webinar_header = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('webinar_description', blocks.TextBlock()),
                ('link_text', blocks.CharBlock()),
                ('link_href', blocks.URLBlock())
            ]))], max_num=1), use_json_field=True)

    os_textbook_heading = models.TextField(blank=True, null=True)
    os_textbook_categories = StreamField([
        ('category', blocks.ListBlock(blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('text', blocks.TextBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    about_os = StreamField([
        ('content', AboutOpenStaxBlock()),
    ], use_json_field=True)

    info_boxes = StreamField([
        ('info_box', blocks.ListBlock(InfoBoxBlock())),
    ], use_json_field=True)
    book_categories_heading = models.TextField(default='')
    learn_more_heading = models.TextField(default='')
    learn_more_blog_posts = models.TextField(default='')
    learn_more_webinars = models.TextField(default='')
    learn_more_about_books = models.TextField(default='')

    philanthropic_support = models.TextField(blank=True, null=True)
    translations = StreamField([
        ('translation', blocks.ListBlock(blocks.StructBlock([
            ('locale', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /subjects
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/subjects/{}'.format(self.slug[0:-6])

    @property
    def selected_subject(self):
        return self.subject.all()

    @property
    def subjects(self):
        subject_list = {}
        for subject in snippets.Subject.objects.filter(name=str(self.selected_subject[0].subject_name)):
            subject_categories = {}
            categories = {}

            subject_categories['icon'] = subject.subject_icon
            all_books = [book for book in Book.objects.all().order_by('title') if subject.name in book.subjects()]
            for category in snippets.SubjectCategory.objects.filter(subject_id=subject.id).order_by('subject_category'):
                books = {}
                book_list = {}
                for book in all_books:
                    if book.subject_categories is not None \
                            and category.subject_category in book.subject_categories \
                            and book.book_state not in ['retired', 'unlisted']:
                        book_data = []
                        book_data.append({
                            'id': book.id,
                            'slug': 'books/{}'.format(book.slug),
                            'book_state': book.book_state,
                            'title': book.title,
                            'subjects': book.subjects(),
                            'subject_categories': book.subject_categories,
                            'k12subject': book.k12subjects(),
                            'is_ap': book.is_ap,
                            'cover_url': book.cover_url,
                            'cover_color': book.cover_color,
                            'high_resolution_pdf_url': book.high_resolution_pdf_url,
                            'low_resolution_pdf_url': book.low_resolution_pdf_url,
                            'ibook_link': book.ibook_link,
                            'ibook_link_volume_2': book.ibook_link_volume_2,
                            'webview_link': book.webview_link,
                            'webview_rex_link': book.webview_rex_link,
                            'bookshare_link': book.bookshare_link,
                            'kindle_link': book.kindle_link,
                            'amazon_coming_soon': book.amazon_coming_soon,
                            'amazon_link': book.amazon_link,
                            'bookstore_coming_soon': book.bookstore_coming_soon,
                            'comp_copy_available': book.comp_copy_available,
                            'salesforce_abbreviation': book.salesforce_abbreviation,
                            'salesforce_name': book.salesforce_name,
                            'urls': book.book_urls(),
                            'last_updated_pdf': book.last_updated_pdf,
                        })
                        books[book.title] = book_data
                book_list['category_description'] = category.description
                book_list['books'] = books
                categories[category.subject_category] = book_list
            subject_categories['categories'] = categories
            subject_list[subject.name] = subject_categories

        return subject_list

    api_fields = [
        APIField('page_description'),
        APIField('tutor_ad'),
        APIField('blog_header'),
        APIField('webinar_header'),
        APIField('os_textbook_heading'),
        APIField('os_textbook_categories'),
        APIField('about_os'),
        APIField('info_boxes'),
        APIField('book_categories_heading'),
        APIField('learn_more_heading'),
        APIField('learn_more_blog_posts'),
        APIField('learn_more_webinars'),
        APIField('learn_more_about_books'),
        APIField('philanthropic_support'),
        APIField('subjects'),
        APIField('translations'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([InlinePanel("subject", label="Subject", min_num=1, max_num=1)], heading="Subject(s)"),
        FieldPanel('page_description'),
        FieldPanel('tutor_ad'),
        FieldPanel('blog_header'),
        FieldPanel('webinar_header'),
        FieldPanel('os_textbook_heading'),
        FieldPanel('os_textbook_categories'),
        FieldPanel('about_os'),
        FieldPanel('info_boxes'),
        FieldPanel('book_categories_heading'),
        FieldPanel('learn_more_heading'),
        FieldPanel('learn_more_blog_posts'),
        FieldPanel('learn_more_webinars'),
        FieldPanel('learn_more_about_books'),
        FieldPanel('philanthropic_support'),
        FieldPanel('translations'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.Subjects']

    class Meta:
        verbose_name = "Subject Page"


class FormHeadings(Page):
    adoption_intro_heading = models.CharField(max_length=255)
    adoption_intro_description = RichTextField()
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
        APIField('adoption_intro_description'),
        APIField('interest_intro_heading'),
        APIField('interest_intro_description'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = [
        TitleFieldPanel('title'),
        FieldPanel('adoption_intro_heading'),
        FieldPanel('adoption_intro_description'),
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
    parent_page_types = ['pages.HomePage']
    max_count = 1


class K12Subject(Page):
    subheader = models.TextField(default='HIGH SCHOOL')
    books_heading = models.TextField(default='')
    books_short_desc = RichTextField(default='')
    about_books_heading = models.TextField(default='About the Books')
    about_books_text = models.CharField(default='FIND SUPPLEMENTAL RESOURCES', blank=True, max_length=255)
    adoption_heading = models.TextField(default='Using an OpenStax resource in your classroom? Let us know!')
    adoption_text = RichTextField(
        default="<p>Help us continue to make high-quality educational materials accessible by letting us know you've adopted! Our future grant funding is based on educator adoptions and the number of students we impact.</p>")
    adoption_link_text = models.CharField(default='Report Your Adoption', max_length=255)
    adoption_link = models.URLField(blank=True, default='/adoption')
    quote_heading = models.TextField(default='What Our Teachers Say', blank=True, )
    quote_text = models.CharField(default='', blank=True, max_length=255)
    resources_heading = models.TextField(default='Supplemental Resources')
    blogs_heading = models.TextField(default='Blogs for High School Teachers', blank=True, )
    rfi_heading = models.TextField(default="Don't see what you're looking for?")
    rfi_text = models.CharField(
        default="We're here to answer any questions you may have. Complete the form to get in contact with a member of our team.",
        max_length=255)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def subject_intro(self):
        for subject in snippets.K12Subject.objects.filter(locale=self.locale, name=self.title).order_by('name'):
            subject_intro = subject.intro_text
        return subject_intro

    @property
    def subject_image(self):
        for subject in snippets.K12Subject.objects.filter(locale=self.locale, name=self.title).order_by('name'):
            subject_image = subject.subject_image
        return subject_image

    @property
    def subject_category(self):
        for subject in snippets.K12Subject.objects.filter(locale=self.locale, name=self.title).order_by('name'):
            subject_category = subject.subject_category
        return subject_category

    @property
    def books(self):
        books = Book.objects.order_by('path')
        book_data = []
        for book in books:
            k12subjects = []
            for subject in book.k12book_subjects.all():
                k12subjects.append(subject.subject_name)
            subjects = []
            for subject in book.book_subjects.all():
                subjects.append(subject.subject_name)
            if book.k12book_subjects is not None \
                    and self.title in k12subjects \
                    and book.book_state not in ['retired', 'draft']:
                book_data.append({
                    'id': book.id,
                    'slug': 'books/{}'.format(book.slug),
                    'title': book.title,
                    'description': book.description,
                    'cover_url': book.cover_url,
                    'is_ap': book.is_ap,
                    'is_hs': 'High School' in subjects,
                    'cover_color': book.cover_color,
                    'high_resolution_pdf_url': book.high_resolution_pdf_url,
                    'low_resolution_pdf_url': book.low_resolution_pdf_url,
                    'ibook_link': book.ibook_link,
                    'ibook_link_volume_2': book.ibook_link_volume_2,
                    'webview_link': book.webview_link,
                    'webview_rex_link': book.webview_rex_link,
                    'bookshare_link': book.bookshare_link,
                    'kindle_link': book.kindle_link,
                    'amazon_coming_soon': book.amazon_coming_soon,
                    'amazon_link': book.amazon_link,
                    'bookstore_coming_soon': book.bookstore_coming_soon,
                    'comp_copy_available': book.comp_copy_available,
                    'salesforce_abbreviation': book.salesforce_abbreviation,
                    'salesforce_name': book.salesforce_name,
                    'urls': book.book_urls(),
                    'updated': book.updated,
                    'created': book.created,
                    'publish_date': book.publish_date,
                    'last_updated_pdf': book.last_updated_pdf
                })
        return book_data

    def student_resource_headers(self):
        student_resource_data = []
        book_ids = {}
        for book in self.books:
            book_id = book.get('id')
            book_title = book.get('title')
            book_ids[book_id] = book_title
        for resource in BookStudentResources.objects.filter(display_on_k12=True,
                                                            book_student_resource_id__in=book_ids).all():
            link_document_url = None
            if resource.link_document_id is not None:
                link_document_url = resource.link_document_url
            student_resource_data.append({
                'id': resource.id,
                'heading': resource.get_resource_heading(),
                'icon': resource.get_resource_icon(),
                'book': book_ids[resource.book_student_resource_id],
                'resource_id': resource.resource_id,
                'resource_unlocked': resource.resource_unlocked,
                'link_external': resource.link_external,
                'link_page': resource.link_page,
                'link_document_url': link_document_url,
                'link_text': resource.link_text,
                'coming_soon_text': resource.coming_soon_text,
                'updated': resource.updated,
                'print_link': resource.print_link,
                'display_on_k12': resource.display_on_k12,
                'resource_category': resource.resource_category,
            })
        return student_resource_data

    def faculty_resource_headers(self):
        faculty_resource_data = []
        book_ids = {}
        for book in self.books:
            book_id = book.get('id')
            book_title = book.get('title')
            book_ids[book_id] = book_title
        for resource in BookFacultyResources.objects.filter(display_on_k12=True,
                                                            book_faculty_resource_id__in=book_ids).all():
            link_document_url = None
            if resource.link_document_id is not None:
                link_document_url = resource.link_document_url
            faculty_resource_data.append({
                'id': resource.id,
                'heading': resource.get_resource_heading(),
                'icon': resource.get_resource_icon(),
                'book': book_ids[resource.book_faculty_resource_id],
                'resource_id': resource.resource_id,
                'resource_unlocked': resource.resource_unlocked,
                'link_external': resource.link_external,
                'link_page_id': resource.link_page_id,
                'link_document_url': link_document_url,
                'link_text': resource.link_text,
                'coming_soon_text': resource.coming_soon_text,
                'updated': resource.updated,
                'print_link': resource.print_link,
                'k12': resource.k12,
                'display_on_k12': resource.display_on_k12,
                'resource_category': resource.resource_category,
            })
        return faculty_resource_data

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/k12/{}'.format(self.slug[4:])

    api_fields = [
        APIField('subheader'),
        APIField('subject_intro'),
        APIField('subject_image'),
        APIField('subject_category'),
        APIField('books_heading'),
        APIField('books_short_desc'),
        APIField('about_books_heading'),
        APIField('about_books_text'),
        APIField('books'),
        APIField('student_resource_headers'),
        APIField('faculty_resource_headers'),
        APIField('adoption_heading'),
        APIField('adoption_text'),
        APIField('adoption_link_text'),
        APIField('adoption_link'),
        APIField('quote_heading'),
        APIField('quote_text'),
        APIField('resources_heading'),
        APIField('blogs_heading'),
        APIField('rfi_heading'),
        APIField('rfi_text'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('subheader'),
        FieldPanel('books_heading'),
        FieldPanel('books_short_desc'),
        FieldPanel('about_books_heading'),
        FieldPanel('about_books_text'),
        FieldPanel('adoption_heading'),
        FieldPanel('adoption_text'),
        FieldPanel('adoption_link_text'),
        FieldPanel('adoption_link'),
        FieldPanel('quote_heading'),
        FieldPanel('quote_text'),
        FieldPanel('resources_heading'),
        FieldPanel('blogs_heading'),
        FieldPanel('rfi_heading'),
        FieldPanel('rfi_text'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.K12MainPage']

    class Meta:
        verbose_name = "K12 Subject"


class AllyLogos(Page):
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
        APIField('description'),
        APIField('ally_logos_heading'),
        APIField('ally_logos_description'),
        APIField('ally_logos'),
        APIField('book_ally_logos_heading'),
        APIField('book_ally_logos_description'),
        APIField('book_ally_logos'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'
    parent_page_types = ['pages.HomePage']


class Assignable(Page):
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
        APIField('heading_description'),
        APIField('add_assignable_cta_header'),
        APIField('add_assignable_cta_description'),
        APIField('add_assignable_cta_link'),
        APIField('add_assignable_cta_button_text'),
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
