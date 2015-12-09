from django.db import models
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                MultiFieldPanel,
                                                PageChooserPanel,
                                                StreamFieldPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import TextBlock, ChooserBlock, StructBlock, ListBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, PageChooserBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from modelcluster.fields import ParentalKey


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(('left','Wrap left'),('right','Wrap right'),('mid','Mid width'),('full','Full width'),))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(('normal','Normal'),('full','Full width'),))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class CommonStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(icon="image", label="Aligned image")
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")
    page = PageChooserBlock(icon="doc-full-inverse", label="Internal Link")


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


class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True
        
# Home Page

class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('pages.HomePage', related_name='carousel_items')


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('pages.HomePage', related_name='related_links')


class HomePage(Page):
    body = StreamField(CommonStreamBlock())
    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )
    
    api_fields = ('body', )

    class Meta:
        verbose_name = "Website Page"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    StreamFieldPanel('body'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
]
