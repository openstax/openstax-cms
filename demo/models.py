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



EVENT_AUDIENCE_CHOICES = (
    ('public', "Public"),
    ('private', "Private"),
)

# Global Streamfield definition

class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"

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

class DemoStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")


# A couple of abstract classes that contain commonly used fields

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


class ContactFields(models.Model):
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    post_code = models.CharField(max_length=10, blank=True)

    panels = [
        FieldPanel('telephone'),
        FieldPanel('email'),
        FieldPanel('address_1'),
        FieldPanel('address_2'),
        FieldPanel('city'),
        FieldPanel('country'),
        FieldPanel('post_code'),
    ]

    class Meta:
        abstract = True


# Carousel items

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


# Related links

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Advert Snippet

class AdvertPlacement(models.Model):
    page = ParentalKey('wagtailcore.Page', related_name='advert_placements')
    advert = models.ForeignKey('demo.Advert', related_name='+')


class Advert(models.Model):
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='adverts',
        null=True,
        blank=True
    )
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('page'),
        FieldPanel('url'),
        FieldPanel('text'),
    ]

    def __unicode__(self):
        return self.text

register_snippet(Advert)


# Home Page

class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.HomePage', related_name='carousel_items')


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.HomePage', related_name='related_links')


class HomePage(Page):
    body = StreamField(DemoStreamBlock())
    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    class Meta:
        verbose_name = "Homepage"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    StreamFieldPanel('body'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
]

HomePage.promote_panels = Page.promote_panels


# Standard index page

class StandardIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.StandardIndexPage', related_name='related_links')


class StandardIndexPage(Page):
    intro = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
    )

StandardIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

StandardIndexPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]


# Standard page

class StandardPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.StandardPage', related_name='carousel_items')


class StandardPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.StandardPage', related_name='related_links')


class StandardPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
        index.SearchField('body'),
    )

StandardPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('carousel_items', label="Carousel items"),
    FieldPanel('body', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

StandardPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]

# Person page

class PersonPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.PersonPage', related_name='related_links')


class PersonPage(Page, ContactFields):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    intro = RichTextField(blank=True)
    biography = RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('first_name'),
        index.SearchField('last_name'),
        index.SearchField('intro'),
        index.SearchField('biography'),
    )

PersonPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('first_name'),
    FieldPanel('last_name'),
    FieldPanel('intro', classname="full"),
    FieldPanel('biography', classname="full"),
    ImageChooserPanel('image'),
    MultiFieldPanel(ContactFields.panels, "Contact"),
    InlinePanel('related_links', label="Related links"),
]

PersonPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]


# Contact page

class ContactPage(Page, ContactFields):
    body = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

ContactPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    MultiFieldPanel(ContactFields.panels, "Contact"),
]

ContactPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]
