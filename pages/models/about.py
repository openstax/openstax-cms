from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.api import APIField

from openstax.api_fields import ExpandedRichTextField
from openstax.functions import build_image_url
from openstax.preview import FrontendPreviewMixin


from pages.custom_blocks import ImageBlock, \
    APIImageChooserBlock, \
    APIRichTextBlock

from .bases import Group



class AboutUsPage(FrontendPreviewMixin, Page):
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
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class OpenStaxPeople(Orderable, Group):
    marketing_video = ParentalKey('pages.TeamPage', related_name='openstax_people')


class TeamPage(FrontendPreviewMixin, Page):
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


class LearningResearchPage(FrontendPreviewMixin, Page):
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
                ('research_area_blurb', APIRichTextBlock()),
                ('research_area_blurb_mobile', APIRichTextBlock()),
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
        APIField('research_area_description_mobile', serializer=ExpandedRichTextField()),
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
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class Careers(FrontendPreviewMixin, Page):
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
        APIField('careers_content', serializer=ExpandedRichTextField()),
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
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


