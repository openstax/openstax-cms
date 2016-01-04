from django.db import models
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                MultiFieldPanel,
                                                PageChooserPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import TextBlock, ChooserBlock, StructBlock, ListBlock, FieldBlock, CharBlock, RichTextBlock, PageChooserBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from modelcluster.fields import ParentalKey


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(('left','Wrap left'),('right','Wrap right'),('mid','Mid width'),('full','Full width'),))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(('normal','Normal'),('full','Full width'),))


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
    page_header = models.CharField(max_length=255)
    introduction = RichTextField()
    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    api_fields = ('page_header', 'introduction', 'intro_image')

    class Meta:
        verbose_name = "Home Page"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('page_header'),
    ImageChooserPanel('intro_image'),
    FieldPanel('introduction'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
]


class HigherEducationCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('pages.HomePage', related_name='higher_education_carousel_items')
    
    
class HigherEducation(Page):
    classroom_text = RichTextField()

HigherEducation.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
    InlinePanel('higher_education_carousel_items', label="Carousel items"),
]

class K12(Page):
    classroom_text = RichTextField()

K12.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class Books(Page):
    classroom_text = RichTextField()

Books.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class BookDetail(Page):
    classroom_text = RichTextField()

BookDetail.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class Products(Page):
    classroom_text = RichTextField()

Products.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class Research(Page):
    classroom_text = RichTextField()

Research.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class News(Page):
    classroom_text = RichTextField()

News.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class NewsArticle(Page):
    classroom_text = RichTextField()

NewsArticle.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class ContactUs(Page):
    classroom_text = RichTextField()

ContactUs.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class AboutUs(Page):
    classroom_text = RichTextField()

AboutUs.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class Give(Page):
    classroom_text = RichTextField()

Give.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class Adopters(Page):
    classroom_text = RichTextField()

Adopters.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class EcosystemAllies(Page):
    classroom_text = RichTextField()

EcosystemAllies.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

class AdoptionForm(Page):
    classroom_text = RichTextField()

AdoptionForm.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('classroom_text'),
]

#class GeneralHTMLPage(Page): #this will be used for confirmations/forms from sales force, these won't be editable
