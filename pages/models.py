import json
from django import forms
from django.db import models
from django.http.response import JsonResponse, HttpResponse
from django.http import Http404
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel,
                                                MultiFieldPanel,
                                                PageChooserPanel,
                                                StreamFieldPanel)
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailcore.blocks import FieldBlock, RawHTMLBlock, StructBlock
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from openstax.functions import build_image_url


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(
        choices=(('normal', 'Normal'), ('full', 'Full width'),))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class StrategicAdvisors(LinkFields):
    name = models.CharField(max_length=255, help_text="Strategic Advisor Name")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_advisor_image(self):
        return build_image_url(self.image)

    advisor_image = property(get_advisor_image)

    description = RichTextField()

    api_fields = ('name', 'advisor_image', 'description', )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('image'),
        FieldPanel('description'),
    ]


class OpenStaxTeam(LinkFields):
    name = models.CharField(max_length=255, help_text="Team Member Name")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_team_member_image(self):
        return build_image_url(self.image)
    team_member_image = property(get_team_member_image)

    position = models.CharField(max_length=255)
    description = RichTextField()

    api_fields = ('name', 'team_member_image', 'position', 'description', )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('image'),
        FieldPanel('position'),
        FieldPanel('description'),
    ]


class PersonBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True)
    position = blocks.CharBlock(required=True)
    photo = ImageBlock()
    biography = blocks.RichTextBlock()

    class Meta:
        icon = 'user'


class ContentListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)
    description = blocks.RichTextBlock()
    cta = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = 'list-ol'


class ContentBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    image = ImageBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    cta = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    hidden = blocks.BooleanBlock(required=False)

    class Meta:
        icon = 'placeholder'


class QuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock()
    author = blocks.CharBlock()

class AboutUsStrategicAdvisors(Orderable, StrategicAdvisors):
    page = ParentalKey('pages.AboutUs', related_name='strategic_advisors')


class AboutUsOpenStaxTeam(Orderable, OpenStaxTeam):
    page = ParentalKey('pages.AboutUs', related_name='openstax_team')


class AboutUs(Page):
    tagline = models.CharField(max_length=255)
    intro_heading = models.CharField(max_length=255)
    intro_paragraph = RichTextField()
    our_team_heading = models.CharField(max_length=255)

    api_fields = (
        'tagline',
        'intro_heading',
        'intro_paragraph',
        'our_team_heading',
        'openstax_team',
        'strategic_advisors',
        'slug',
        'seo_title',
        'search_description',)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tagline'),
        FieldPanel('intro_heading'),
        FieldPanel('intro_paragraph'),
        FieldPanel('our_team_heading'),
        InlinePanel('openstax_team', label="OpenStax Team"),
        InlinePanel('strategic_advisors', label="Strategic Advisors"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class Allies(LinkFields):
    heading = models.CharField(max_length=255)
    description = RichTextField()
    link_url = models.URLField(blank=True, help_text="Call to Action Link")
    link_text = models.CharField(
        max_length=255, help_text="Call to Action Text")

    api_fields = ('heading', 'description', 'link_url', 'link_text', )

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('link_url'),
        FieldPanel('link_text'),
    ]


class Quote(models.Model):
    IMAGE_ALIGNMENT_CHOICES = (
        ('L', 'left'),
        ('R', 'right'),
        ('F', 'full'),
    )
    quote_text = RichTextField()

    quote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_quote_image(self):
        return build_image_url(self.quote_image)
    quote_image_url = property(get_quote_image)

    quote_image_alignment = models.CharField(max_length=1,
                                             choices=IMAGE_ALIGNMENT_CHOICES,
                                             blank=True,
                                             null=True)
    quote_link = models.URLField(blank=True, null=True)
    quote_link_text = models.CharField(max_length=255, blank=True, null=True)

    api_fields = (
        'quote_text',
        'quote_image_url',
        'get_quote_image_alignment_display',
        'quote_link',
        'quote_link_text',
    )

    panels = [
        FieldPanel('quote_text'),
        ImageChooserPanel('quote_image'),
        FieldPanel('quote_image_alignment'),
        FieldPanel('quote_link'),
        FieldPanel('quote_link_text'),
    ]


# Home Page
class HomePage(Page):
    ALIGNMENT_CHOICES = (
        (u'L', u'Left'),
        (u'R', u'Right'),
    )

    row_0_box_1_content = RichTextField(blank=True, null=True)
    row_0_box_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_0_box_1_image(self):
        return build_image_url(self.row_0_box_1_image)
    row_0_box_1_image_url = property(get_row_0_box_1_image)

    row_0_box_1_image_alignment = models.CharField(max_length=1, choices=ALIGNMENT_CHOICES,
                                                   blank=True, null=True)
    row_0_box_1_cta = models.CharField(max_length=255, blank=True, null=True)
    row_0_box_1_link = models.URLField(blank=True, null=True)

    row_0_box_2_content = RichTextField(blank=True, null=True)
    row_0_box_2_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_0_box_2_image(self):
        return build_image_url(self.row_0_box_2_image)
    row_0_box_2_image_url = property(get_row_0_box_2_image)

    row_0_box_2_image_alignment = models.CharField(max_length=1, choices=ALIGNMENT_CHOICES,
                                                   blank=True, null=True)
    row_0_box_2_cta = models.CharField(max_length=255, blank=True, null=True)
    row_0_box_2_link = models.URLField(blank=True, null=True)

    row_0_box_3_content = RichTextField(blank=True, null=True)
    row_0_box_3_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_0_box_3_image(self):
        return build_image_url(self.row_0_box_3_image)
    row_0_box_3_image_url = property(get_row_0_box_3_image)

    row_0_box_3_image_alignment = models.CharField(max_length=1, choices=ALIGNMENT_CHOICES,
                                                   blank=True, null=True)
    row_0_box_3_cta = models.CharField(max_length=255, blank=True, null=True)
    row_0_box_3_link = models.URLField(blank=True, null=True)

    row_1_box_1_line_1 = models.CharField(max_length=255)
    row_1_box_1_line_2 = models.CharField(max_length=255)
    row_1_box_1_line_3 = models.CharField(max_length=255)

    row_2_box_1_heading = models.CharField(max_length=255)
    row_2_box_1_description = models.CharField(max_length=255)
    row_2_box_2_heading = models.CharField(max_length=255)
    row_2_box_2_description = models.CharField(max_length=255)

    row_3_box_1_heading = models.CharField(max_length=255, blank=True, null=True)
    row_3_box_1_description = models.CharField(max_length=255, blank=True, null=True)
    row_3_box_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_3_box_1_image(self):
        return build_image_url(self.row_3_box_1_image)
    row_3_box_1_image_url = property(get_row_3_box_1_image)

    row_3_box_1_cta = models.CharField(max_length=255, blank=True, null=True)
    row_3_box_1_link = models.URLField(blank=True, null=True)

    row_4_box_1_heading = models.CharField(max_length=255, blank=True, null=True)
    row_4_box_1_description = models.CharField(max_length=255, blank=True, null=True)
    row_4_box_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_4_box_1_image(self):
        return build_image_url(self.row_4_box_1_image)
    row_4_box_1_image_url = property(get_row_4_box_1_image)

    row_4_box_1_cta = models.CharField(max_length=255, blank=True, null=True)
    row_4_box_1_link = models.URLField(blank=True, null=True)

    row_5_box_1_heading = models.CharField(max_length=255, blank=True, null=True)
    row_5_box_1_description = models.CharField(max_length=255, blank=True, null=True)
    row_5_box_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_5_box_1_image(self):
        return build_image_url(self.row_5_box_1_image)
    row_5_box_1_image_url = property(get_row_5_box_1_image)

    row_5_box_1_cta = models.CharField(max_length=255, blank=True, null=True)
    row_5_box_1_link = models.URLField(blank=True, null=True)

    api_fields = (
        'title',
        'row_0_box_1_content',
        'row_0_box_1_image_url',
        'get_row_0_box_1_image_alignment_display',
        'row_0_box_1_cta',
        'row_0_box_1_link',
        'row_0_box_2_content',
        'row_0_box_2_image_url',
        'get_row_0_box_2_image_alignment_display',
        'row_0_box_2_cta',
        'row_0_box_2_link',
        'row_0_box_3_content',
        'row_0_box_3_image_url',
        'get_row_0_box_3_image_alignment_display',
        'row_0_box_3_cta',
        'row_0_box_3_link',
        'row_1_box_1_line_1',
        'row_1_box_1_line_2',
        'row_1_box_1_line_3',
        'row_2_box_1_heading',
        'row_2_box_1_description',
        'row_2_box_2_heading',
        'row_2_box_2_description',
        'row_3_box_1_heading',
        'row_3_box_1_description',
        'row_3_box_1_image_url',
        'row_3_box_1_cta',
        'row_3_box_1_link',
        'row_4_box_1_heading',
        'row_4_box_1_description',
        'row_4_box_1_image_url',
        'row_4_box_1_cta',
        'row_4_box_1_link',
        'row_5_box_1_heading',
        'row_5_box_1_description',
        'row_5_box_1_image_url',
        'row_5_box_1_cta',
        'row_5_box_1_link',
        'slug',
        'seo_title',
        'search_description',)

    class Meta:
        verbose_name = "Home Page"

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('row_0_box_1_content'),
        ImageChooserPanel('row_0_box_1_image'),
        FieldPanel('row_0_box_1_image_alignment'),
        FieldPanel('row_0_box_1_cta'),
        FieldPanel('row_0_box_1_link'),
        FieldPanel('row_0_box_2_content'),
        ImageChooserPanel('row_0_box_2_image'),
        FieldPanel('row_0_box_2_image_alignment'),
        FieldPanel('row_0_box_2_cta'),
        FieldPanel('row_0_box_2_link'),
        FieldPanel('row_0_box_3_content'),
        ImageChooserPanel('row_0_box_3_image'),
        FieldPanel('row_0_box_3_image_alignment'),
        FieldPanel('row_0_box_3_cta'),
        FieldPanel('row_0_box_3_link'),
        FieldPanel('row_1_box_1_line_1'),
        FieldPanel('row_1_box_1_line_2'),
        FieldPanel('row_1_box_1_line_3'),
        FieldPanel('row_2_box_1_heading'),
        FieldPanel('row_2_box_1_description'),
        FieldPanel('row_2_box_2_heading'),
        FieldPanel('row_2_box_2_description'),
        FieldPanel('row_3_box_1_heading'),
        FieldPanel('row_3_box_1_description'),
        ImageChooserPanel('row_3_box_1_image'),
        FieldPanel('row_3_box_1_cta'),
        FieldPanel('row_3_box_1_link'),
        FieldPanel('row_4_box_1_heading'),
        FieldPanel('row_4_box_1_description'),
        ImageChooserPanel('row_4_box_1_image'),
        FieldPanel('row_4_box_1_cta'),
        FieldPanel('row_4_box_1_link'),
        FieldPanel('row_5_box_1_heading'),
        FieldPanel('row_5_box_1_description'),
        ImageChooserPanel('row_5_box_1_image'),
        FieldPanel('row_5_box_1_cta'),
        FieldPanel('row_5_box_1_link'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    # we are controlling what types of pages are allowed under a homepage
    # if a new page type is created, it needs to be added here to show up in
    # the admin
    subpage_types = [
        'pages.HigherEducation',
        'pages.ContactUs',
        'pages.AboutUs',
        'pages.GeneralPage',
        'pages.Adopters',
        'pages.EcosystemAllies',
        'books.BookIndex',
        'news.NewsIndex',
        'allies.Ally',
    ]


class HigherEducationAllies(Orderable, Allies):
    page = ParentalKey(
        'pages.HigherEducation', related_name='higher_education_allies')


class HigherEducation(Page):
    ALIGNMENT_CHOICES = (
        (u'L', u'left'),
        (u'R', u'right'),
    )

    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()

    row_0_box_1_content = RichTextField(blank=True, null=True)
    row_0_box_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_0_box_1_image(self):
        return build_image_url(self.row_0_box_1_image)
    row_0_box_1_image_url = property(get_row_0_box_1_image)

    row_0_box_1_image_alignment = models.CharField(max_length=1, choices=ALIGNMENT_CHOICES,
                                                   blank=True, null=True)
    row_0_box_1_cta = models.CharField(max_length=255, blank=True, null=True)
    row_0_box_1_link = models.URLField(blank=True, null=True)

    row_0_box_2_content = RichTextField(blank=True, null=True)
    row_0_box_2_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_0_box_2_image(self):
        return build_image_url(self.row_0_box_2_image)
    row_0_box_2_image_url = property(get_row_0_box_2_image)

    row_0_box_2_image_alignment = models.CharField(max_length=1, choices=ALIGNMENT_CHOICES,
                                                   blank=True, null=True)
    row_0_box_2_cta = models.CharField(max_length=255, blank=True, null=True)
    row_0_box_2_link = models.URLField(blank=True, null=True)

    row_0_box_3_content = RichTextField(blank=True, null=True)
    row_0_box_3_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_0_box_3_image(self):
        return build_image_url(self.row_0_box_3_image)
    row_0_box_3_image_url = property(get_row_0_box_3_image)

    row_0_box_3_image_alignment = models.CharField(max_length=1, choices=ALIGNMENT_CHOICES,
                                                   blank=True, null=True)
    row_0_box_3_cta = models.CharField(max_length=255, blank=True, null=True)
    row_0_box_3_link = models.URLField(blank=True, null=True)

    get_started_heading = models.CharField(max_length=255)

    get_started_step_1_heading = models.CharField(max_length=255)
    get_started_step_1_description = RichTextField()
    get_started_step_1_cta = models.CharField(max_length=255)

    get_started_step_2_heading = models.CharField(max_length=255)
    get_started_step_2_description = RichTextField()
    get_started_step_2_cta = models.CharField(max_length=255)

    get_started_step_3_heading = models.CharField(max_length=255)
    get_started_step_3_description = RichTextField()
    get_started_step_3_cta = models.CharField(max_length=255)

    adopt_heading = models.CharField(max_length=255)
    adopt_description = RichTextField()
    adopt_cta = models.CharField(max_length=255)

    row_1_box_1_heading = models.CharField(max_length=255)
    row_1_box_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_1_box_1_image(self):
        return build_image_url(self.row_1_box_1_image)
    row_1_box_1_image_url = property(get_row_1_box_1_image)

    row_1_box_1_description = RichTextField()
    row_1_box_1_cta = models.CharField(max_length=255)
    row_1_box_1_link = models.URLField(blank=True, null=True)

    row_1_box_2_heading = models.CharField(max_length=255)
    row_1_box_2_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_1_box_2_image(self):
        return build_image_url(self.row_1_box_2_image)
    row_1_box_2_image_url = property(get_row_1_box_2_image)

    row_1_box_2_description = RichTextField()
    row_1_box_2_cta = models.CharField(max_length=255)
    row_1_box_2_link = models.URLField(blank=True, null=True)

    row_1_box_3_heading = models.CharField(max_length=255)
    row_1_box_3_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_row_1_box_3_image(self):
        return build_image_url(self.row_1_box_3_image)
    row_1_box_3_image_url = property(get_row_1_box_3_image)

    row_1_box_3_description = RichTextField()
    row_1_box_3_cta = models.CharField(max_length=255)
    row_1_box_3_link = models.URLField(blank=True, null=True)

    row_2_box_1_heading = models.CharField(max_length=255)
    row_2_box_1_description = RichTextField()
    row_2_box_1_cta = models.CharField(max_length=255)
    row_2_box_1_link = models.URLField(blank=True, null=True)

    row_2_box_2_heading = models.CharField(max_length=255)
    row_2_box_2_description = RichTextField()
    row_2_box_2_cta = models.CharField(max_length=255)
    row_2_box_2_link = models.URLField(blank=True, null=True)

    api_fields = (
        'intro_heading',
        'intro_description',
        'row_0_box_1_content',
        'row_0_box_1_image_url',
        'get_row_0_box_1_image_alignment_display',
        'row_0_box_1_cta',
        'row_0_box_1_link',
        'row_0_box_2_content',
        'row_0_box_2_image_url',
        'get_row_0_box_2_image_alignment_display',
        'row_0_box_2_cta',
        'row_0_box_2_link',
        'row_0_box_3_content',
        'row_0_box_3_image_url',
        'get_row_0_box_3_image_alignment_display',
        'row_0_box_3_cta',
        'row_0_box_3_link',
        'get_started_heading',
        'get_started_step_1_heading',
        'get_started_step_1_description',
        'get_started_step_1_cta',
        'get_started_step_2_heading',
        'get_started_step_2_description',
        'get_started_step_2_cta',
        'get_started_step_3_heading',
        'get_started_step_3_description',
        'get_started_step_3_cta',
        'adopt_heading',
        'adopt_description',
        'adopt_cta',
        'row_1_box_1_heading',
        'row_1_box_1_image_url',
        'row_1_box_1_description',
        'row_1_box_1_cta',
        'row_1_box_1_link',
        'row_1_box_2_heading',
        'row_1_box_2_image_url',
        'row_1_box_2_description',
        'row_1_box_2_cta',
        'row_1_box_2_link',
        'row_1_box_3_heading',
        'row_1_box_3_image_url',
        'row_1_box_3_description',
        'row_1_box_3_cta',
        'row_1_box_3_link',
        'row_2_box_1_heading',
        'row_2_box_1_description',
        'row_2_box_1_cta',
        'row_2_box_1_link',
        'row_2_box_2_heading',
        'row_2_box_2_description',
        'row_2_box_2_cta',
        'row_2_box_2_link',
        'slug',
        'seo_title',
        'search_description',)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('row_0_box_1_content'),
        ImageChooserPanel('row_0_box_1_image'),
        FieldPanel('row_0_box_1_image_alignment'),
        FieldPanel('row_0_box_1_cta'),
        FieldPanel('row_0_box_1_link'),
        FieldPanel('row_0_box_2_content'),
        ImageChooserPanel('row_0_box_2_image'),
        FieldPanel('row_0_box_2_image_alignment'),
        FieldPanel('row_0_box_2_cta'),
        FieldPanel('row_0_box_2_link'),
        FieldPanel('row_0_box_3_content'),
        ImageChooserPanel('row_0_box_3_image'),
        FieldPanel('row_0_box_3_image_alignment'),
        FieldPanel('row_0_box_3_cta'),
        FieldPanel('row_0_box_3_link'),
        FieldPanel('get_started_heading'),
        FieldPanel('get_started_step_1_heading'),
        FieldPanel('get_started_step_1_description'),
        FieldPanel('get_started_step_1_cta'),
        FieldPanel('get_started_step_2_heading'),
        FieldPanel('get_started_step_2_description'),
        FieldPanel('get_started_step_2_cta'),
        FieldPanel('get_started_step_3_heading'),
        FieldPanel('get_started_step_3_description'),
        FieldPanel('get_started_step_3_cta'),
        FieldPanel('adopt_heading'),
        FieldPanel('adopt_description'),
        FieldPanel('adopt_cta'),
        FieldPanel('row_1_box_1_heading'),
        ImageChooserPanel('row_1_box_1_image'),
        FieldPanel('row_1_box_1_description'),
        FieldPanel('row_1_box_1_cta'),
        FieldPanel('row_1_box_1_link'),
        FieldPanel('row_1_box_2_heading'),
        ImageChooserPanel('row_1_box_2_image'),
        FieldPanel('row_1_box_2_description'),
        FieldPanel('row_1_box_2_cta'),
        FieldPanel('row_1_box_2_link'),
        FieldPanel('row_1_box_3_heading'),
        ImageChooserPanel('row_1_box_3_image'),
        FieldPanel('row_1_box_3_description'),
        FieldPanel('row_1_box_3_cta'),
        FieldPanel('row_1_box_3_link'),
        FieldPanel('row_2_box_1_heading'),
        FieldPanel('row_2_box_1_description'),
        FieldPanel('row_2_box_1_cta'),
        FieldPanel('row_2_box_1_link'),
        FieldPanel('row_2_box_2_heading'),
        FieldPanel('row_2_box_2_description'),
        FieldPanel('row_2_box_2_cta'),
        FieldPanel('row_2_box_2_link'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class K12(Page):
    heading = models.CharField(max_length=255)
    description = RichTextField()
    box_1_heading = models.CharField(max_length=255)
    box_1_description = RichTextField()
    box_2_heading = models.CharField(max_length=255)
    box_2_description = RichTextField()
    box_3_heading = models.CharField(max_length=255)
    box_3_description = RichTextField()
    box_4_heading = models.CharField(max_length=255)
    box_4_description = RichTextField()
    box_5_heading = models.CharField(max_length=255)
    box_5_description = RichTextField()

    api_fields = (
        'heading',
        'description',
        'box_1_heading',
        'box_1_description',
        'box_2_heading',
        'box_2_description',
        'box_3_heading',
        'box_3_description',
        'box_4_heading',
        'box_4_description',
        'box_5_heading',
        'box_5_description',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('box_1_heading'),
        FieldPanel('box_1_description'),
        FieldPanel('box_2_heading'),
        FieldPanel('box_2_description'),
        FieldPanel('box_3_heading'),
        FieldPanel('box_3_description'),
        FieldPanel('box_4_heading'),
        FieldPanel('box_4_description'),
        FieldPanel('box_5_heading'),
        FieldPanel('box_5_description'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class ProductsAllies(Orderable, Allies):
    page = ParentalKey('pages.Products', related_name='products_allies')


class Products(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()
    tutor_heading = models.CharField(max_length=255)
    tutor_description = RichTextField()
    concept_coach_heading = models.CharField(max_length=255)
    concept_coach_description = RichTextField()
    cnx_heading = models.CharField(max_length=255)
    cnx_description = RichTextField()
    allies_heading = models.CharField(max_length=255)
    allies_description = RichTextField()

    api_fields = (
        'intro_heading',
        'intro_description',
        'tutor_heading',
        'tutor_description',
        'concept_coach_heading',
        'concept_coach_description',
        'cnx_heading',
        'cnx_description',
        'allies_heading',
        'allies_description',
        'products_allies',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('tutor_heading'),
        FieldPanel('tutor_description'),
        FieldPanel('concept_coach_heading'),
        FieldPanel('concept_coach_description'),
        FieldPanel('cnx_heading'),
        FieldPanel('cnx_description'),
        FieldPanel('allies_heading'),
        FieldPanel('allies_description'),
        InlinePanel('products_allies', label="Allies"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class Research(Page):
    classroom_text = RichTextField()

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('classroom_text'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class ContactUs(Page):
    tagline = models.CharField(max_length=255)
    mailing_header = models.CharField(max_length=255)
    mailing_address = RichTextField()
    phone_number = models.CharField(max_length=255)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tagline'),
        FieldPanel('mailing_header'),
        FieldPanel('mailing_address'),
        FieldPanel('phone_number'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    api_fields = (
        'title',
        'tagline',
        'mailing_header',
        'mailing_address',
        'phone_number',
        'slug',
        'seo_title',
        'search_description',
    )

    parent_page_types = ['pages.HomePage']


class GeneralPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('tagline', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
        ('person', PersonBlock()),
        ('content_row', blocks.StreamBlock(
            [
                ('content_block', ContentBlock()),
                ('quote_block', QuoteBlock()),
            ],
            icon='form'
        )),
        ('list', ContentListBlock()),
    ])

    api_fields = (
        'title',
        'body',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title'),
        StreamFieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']

    def serve(self, request, *args, **kwargs):
        data = {
            'title': self.title,
            'slug': self.slug,
            'seo_title': self.seo_title,
            'search_description': self.search_description,
            'body': json.dump(self.body),
        }
        return JsonResponse(data)


class Give(Page):
    touchnet_form = RawHTMLBlock()

    content_panels = [
        FieldPanel('title', classname="full title"),
        # FieldPanel('touchnet_form'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class Adopters(Page):
    classroom_text = RichTextField()

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('classroom_text'),
    ]

    parent_page_types = ['pages.HomePage']


class EcosystemAllies(Page):
    classroom_text = RichTextField()

    api_fields = (
        'title',
        'classroom_text',
        'slug',
        'seo_title',
        'search_description',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('classroom_text'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']


class AdoptionForm(Page):
    classroom_text = RichTextField()

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('classroom_text'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),

    ]

    parent_page_types = ['pages.HomePage']
