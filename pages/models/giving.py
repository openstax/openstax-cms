from django.db import models
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.api import APIField

from openstax.api_fields import ExpandedRichTextField
from openstax.functions import build_image_url
from openstax.preview import FrontendPreviewMixin
from news.models import BlogStreamBlock  # for use on the ImpactStories


from pages.custom_blocks import ImageBlock, \
    APIImageChooserBlock, \
    StoryBlock, \
    APIRichTextBlock




class Supporters(FrontendPreviewMixin, Page):
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

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class MapPage(FrontendPreviewMixin, Page):
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

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class Give(FrontendPreviewMixin, Page):
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
        APIField('payment_method_1_content', serializer=ExpandedRichTextField()),
        APIField('payment_method_2_heading'),
        APIField('payment_method_2_content', serializer=ExpandedRichTextField()),
        APIField('payment_method_3_heading'),
        APIField('payment_method_3_content', serializer=ExpandedRichTextField()),
        APIField('payment_method_4_heading'),
        APIField('payment_method_4_content', serializer=ExpandedRichTextField()),
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

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class GiveForm(FrontendPreviewMixin, Page):
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

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class ImpactStory(FrontendPreviewMixin, Page):
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


class Impact(FrontendPreviewMixin, Page):
    reach = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('image', ImageBlock()),
                ('heading', blocks.CharBlock()),
                ('description', APIRichTextBlock()),
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
                ('description', APIRichTextBlock()),
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
                ('quote', APIRichTextBlock())
            ]))], max_num=1), use_json_field=True)
    making_a_difference = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('description', APIRichTextBlock()),
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
                ('quote', APIRichTextBlock()),
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


