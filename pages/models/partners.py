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

from salesforce.models import PartnerTypeMapping, PartnerFieldNameMapping, PartnerCategoryMapping, Partner

from pages.custom_blocks import ImageBlock, \
    APIRichTextBlock




class Technology(FrontendPreviewMixin, Page):
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
        APIField('intro_description', serializer=ExpandedRichTextField()),
        APIField('banner_cta'),
        APIField('banner_cta_link'),
        APIField('select_tech_heading'),
        APIField('select_tech_step_1'),
        APIField('select_tech_step_2'),
        APIField('select_tech_step_3'),
        APIField('new_frontier_heading'),
        APIField('new_frontier_subheading'),
        APIField('new_frontier_description', serializer=ExpandedRichTextField()),
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
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class InstitutionalPartnership(FrontendPreviewMixin, Page):
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
            ('description', APIRichTextBlock())
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


class InstitutionalPartnerProgramPage(FrontendPreviewMixin, Page):
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
            ('html', APIRichTextBlock()),
        ])))
    ], use_json_field=True)
    section_3_tall_cards = StreamField([
        ('card', blocks.ListBlock(blocks.StructBlock([
            ('html', APIRichTextBlock()),
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
        APIField('section_1_description', serializer=ExpandedRichTextField()),
        APIField('section_1_link_text'),
        APIField('section_1_link'),
        APIField('section_1_background_image'),
        APIField('quote'),
        APIField('quote_name'),
        APIField('quote_title'),
        APIField('quote_school'),
        APIField('section_2_heading'),
        APIField('section_2_description', serializer=ExpandedRichTextField()),
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
        APIField('section_5_description', serializer=ExpandedRichTextField()),
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
        APIField('section_9_contact_html', serializer=ExpandedRichTextField()),
    ]

    parent_page_type = ['pages.HomePage']
    template = 'page.html'


class PartnersPage(FrontendPreviewMixin, Page):
    heading = models.CharField(max_length=255)
    description = RichTextField()
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
        FieldPanel('header_image'),
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
        APIField('description', serializer=ExpandedRichTextField()),
        APIField('header_image_url'),
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


