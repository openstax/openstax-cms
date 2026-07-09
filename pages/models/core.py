from django.db import models
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail_ai.panels import AIMultipleChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail_html_editor.blocks import EnhancedHTMLBlock
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.api import APIField

from openstax.preview import FrontendPreviewMixin

from salesforce.models import School

from pages.custom_blocks import APIImageChooserBlock, \
    APIRichTextBlock, \
    TEXT_ALIGNMENT_CHOICES

from pages.shared_blocks import LinkInfoBlock, hex_color_block, \
    gradient_config_options, gradient_block_counts, id_config_block


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
            }, required=False, collapsed=True)),
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


class GeneralPage(FrontendPreviewMixin, Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('tagline', blocks.CharBlock(classname="full title")),
        ('paragraph', APIRichTextBlock()),
        ('image', APIImageChooserBlock()),
        ('html', EnhancedHTMLBlock()),
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


