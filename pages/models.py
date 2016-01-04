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


class Funders(LinkFields):
    name = models.CharField(max_length=255, help_text="Funder Name")
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField()
    
    panels = [
        FieldPanel('name'),
        ImageChooserPanel('logo'),
        FieldPanel('description'),
    ]


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
    page = ParentalKey('pages.HigherEducation', related_name='higher_education_carousel_items')
    
    
class HigherEducation(Page):
    intro = RichTextField()
    get_started_step_1 = RichTextField()
    get_started_step_2 = RichTextField()
    get_started_step_3 = RichTextField()
    get_started_step_4 = RichTextField()
    our_books = RichTextField()
    our_impact = RichTextField()
    cnx = RichTextField()
    allies = RichTextField()
    ally_1 = RichTextField()
    ally_2 = RichTextField()
    ally_3 = RichTextField()
    ally_4 = RichTextField()
    ally_5 = RichTextField()

HigherEducation.content_panels = [
    FieldPanel('title', classname="full title"),
    InlinePanel('higher_education_carousel_items', label="Carousel items"),
    FieldPanel('intro'),
    FieldPanel('get_started_step_1'),
    FieldPanel('get_started_step_2'),
    FieldPanel('get_started_step_3'),
    FieldPanel('get_started_step_4'),
    FieldPanel('our_books'),
    FieldPanel('our_impact'),
    FieldPanel('cnx'),
    FieldPanel('allies'),
    FieldPanel('ally_1'),
    FieldPanel('ally_2'),
    FieldPanel('ally_3'),
    FieldPanel('ally_4'),
    FieldPanel('ally_5'),
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
    intro = RichTextField()
    tutor_intro = RichTextField()
    concept_coach_intro = RichTextField()
    cnx_intro = RichTextField()
    allies_intro = RichTextField()
    ally_1 = RichTextField()
    ally_2 = RichTextField()
    ally_3 = RichTextField()
    ally_4 = RichTextField()

Products.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro'),
    FieldPanel('tutor_intro'),
    FieldPanel('concept_coach_intro'),
    FieldPanel('cnx_intro'),
    FieldPanel('allies_intro'),
    FieldPanel('ally_1'),
    FieldPanel('ally_2'),
    FieldPanel('ally_3'),
    FieldPanel('ally_4'),
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


class AboutUsFunders(Orderable, Funders):
    page = ParentalKey('pages.AboutUs', related_name='funders')
    
class AboutUs(Page):
    who_we_are = RichTextField()
    funder_intro = RichTextField()

AboutUs.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('who_we_are'),
    FieldPanel('funder_intro'),
    InlinePanel('funders', label="Funders"),
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
