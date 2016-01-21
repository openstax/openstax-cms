from django.db import models
from django import forms
from django.http import JsonResponse

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                StreamFieldPanel,
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

# NOTE: Consider joining Funders, StrategicAdvisors, and OpenStaxTeam under
# the same superclass in future code updates.

class Funders(LinkFields):
    name = models.CharField(max_length=255, help_text="Funder Name")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField()
    
    api_fields = ('name', 'image', 'description', )
    
    panels = [
        FieldPanel('name'),
        ImageChooserPanel('image'),
        FieldPanel('description'),
    ]
class StrategicAdvisors(LinkFields):
    name = models.CharField(max_length=255, help_text="Strategic Advisor Name")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField()
    
    api_fields = ('name', 'image', 'description', )
    
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
    description = RichTextField()
    
    api_fields = ('name', 'image', 'description', )
    
    panels = [
        FieldPanel('name'),
        ImageChooserPanel('image'),
        FieldPanel('description'),
    ]


class Allies(LinkFields):
    heading = models.CharField(max_length=255) 
    description = RichTextField()
    link_url = models.URLField(blank=True, help_text="Call to Action Link")
    link_text = models.CharField(max_length=255, help_text="Call to Action Text")
    
    api_fields = ('heading', 'description', 'link_url', 'link_text', )
    
    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('link_url'),
        FieldPanel('link_text'),
    ]
    

class Quote(models.Model):
    IMAGE_ALIGNMENT_CHOICES = (
        ('L', 'Left Aligned'),
        ('R', 'Right Aligned'),
        ('F', 'Full Width'),
    )
    quote_text = RichTextField()
    quote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    quote_image_alignment = models.CharField(max_length=1,
                                      choices=IMAGE_ALIGNMENT_CHOICES,
                                      blank=True,
                                      null=True)
    quote_link = models.URLField(blank=True, null=True)
    quote_link_text = models.CharField(max_length=255, blank=True, null=True)
    
    api_fields = (
        'quote_text', 
        'quote_image', 
        'quote_image_alignment', 
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


class HomePageQuotes(Orderable, Quote):
    quote = ParentalKey('pages.HomePage', related_name='homepage_quotes')
    
    
# Home Page
class HomePage(Page):   
    header_2_text = RichTextField()
    higher_ed_heading = models.CharField(max_length=255)
    higher_ed_description = RichTextField()
    k12_heading = models.CharField(max_length=255)
    k12_description = RichTextField()
    give_heading = models.CharField(max_length=255)
    give_description = RichTextField()
    give_cta_link = models.URLField(blank=True)
    give_cta_text = models.CharField(max_length=255)
    adopter_heading = models.CharField(max_length=255)
    adopter_description = RichTextField()
    adopter_cta_link = models.URLField(blank=True)
    adopter_cta_text = models.CharField(max_length=255)
    
    api_fields = (
        'title',
        'homepage_quotes',
        'header_2_text',
        'higher_ed_heading',
        'higher_ed_description',
        'k12_heading',
        'k12_description',
        'give_heading',
        'give_description',
        'give_cta_link',
        'give_cta_text',
        'adopter_heading',
        'adopter_description',
        'adopter_cta_link',
        'adopter_cta_text',
        'slug',
        'seo_title',
        'search_description',)
    
    class Meta:
        verbose_name = "Home Page"

    content_panels = [
        FieldPanel('title', classname="full title"),
        InlinePanel('homepage_quotes', label="Quotes"),
        FieldPanel('header_2_text'),
        FieldPanel('higher_ed_heading'),
        FieldPanel('higher_ed_description'),
        FieldPanel('k12_heading'),
        FieldPanel('k12_description'),
        FieldPanel('give_heading'),
        FieldPanel('give_description'),
        FieldPanel('give_cta_link'),
        FieldPanel('give_cta_text'),
        FieldPanel('adopter_heading'),
        FieldPanel('adopter_description'),
        FieldPanel('adopter_cta_link'),
        FieldPanel('adopter_cta_text'),
    ]
    
    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        
    ]
        
    # we are controlling what types of pages are allowed under a homepage
    # if a new page type is created, it needs to be added here to show up in the admin
    subpage_types = [
        'pages.HigherEducation', 
        'pages.K12',
        'pages.Products',
        'pages.Research',
        'pages.ContactUs',
        'pages.AboutUs',
        'pages.Give',
        'pages.Adopters',
        'pages.EcosystemAllies',
        'pages.AdoptionForm',
        'books.BookIndex',
        'news.NewsIndex',
        ]


class HigherEducationAllies(Orderable, Allies):
    page = ParentalKey('pages.HigherEducation', related_name='higher_education_allies')
    
    
class HigherEducation(Page):
    intro_heading = models.CharField(max_length=255)
    intro_description = RichTextField()
    get_started_heading = models.CharField(max_length=255)
    get_started_step_1_description = RichTextField()
    get_started_step_2_description = RichTextField()
    get_started_step_3_description = RichTextField()
    get_started_step_4_description = RichTextField()
    our_books_heading = models.CharField(max_length=255)
    our_books_description = RichTextField()
    our_impact_heading = models.CharField(max_length=255)
    our_impact_description = RichTextField()
    cnx_heading = models.CharField(max_length=255)
    cnx_description = RichTextField()
    allies_heading = models.CharField(max_length=255)
    allies_description = RichTextField()

    api_fields = (
        'intro_heading', 
        'intro_description', 
        'get_started_heading', 
        'get_started_step_1_description', 
        'get_started_step_2_description', 
        'get_started_step_3_description', 
        'get_started_step_4_description', 
        'our_books_heading', 
        'our_books_description', 
        'our_impact_heading', 
        'our_impact_description', 
        'cnx_heading', 
        'cnx_description', 
        'allies_heading', 
        'allies_description',  
        'higher_education_allies',
        'slug', 
        'seo_title', 
        'search_description',)
    
    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro_heading'),
        FieldPanel('intro_description'),
        FieldPanel('get_started_heading'),
        FieldPanel('get_started_step_1_description'),
        FieldPanel('get_started_step_2_description'),
        FieldPanel('get_started_step_3_description'),
        FieldPanel('get_started_step_4_description'),
        FieldPanel('our_books_heading'),
        FieldPanel('our_books_description'),
        FieldPanel('our_impact_heading'),
        FieldPanel('our_impact_description'),
        FieldPanel('cnx_heading'),
        FieldPanel('cnx_description'),
        FieldPanel('allies_heading'),
        FieldPanel('allies_description'),
        InlinePanel('higher_education_allies', label="Allies"),
    ]
    
    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        
    ]
    
    parent_page_types = ['pages.HomePage']


class K12(Page):
    k12_heading = models.CharField(max_length=255)
    k12_description = RichTextField()
    tutor_heading = models.CharField(max_length=255)
    tutor_description = RichTextField()
    cnx_heading = models.CharField(max_length=255)
    cnx_description = RichTextField()
    allies_heading = models.CharField(max_length=255)
    allies_description = RichTextField()
    
    api_fields = (
        'k12_heading', 
        'k12_description', 
        'tutor_heading', 
        'tutor_description', 
        'cnx_heading', 
        'cnx_description', 
        'allies_heading', 
        'allies_description', 
        'slug', 
        'seo_title', 
        'search_description', 
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('k12_heading'),
        FieldPanel('k12_description'),
        FieldPanel('tutor_heading'),
        FieldPanel('tutor_description'),
        FieldPanel('cnx_heading'),
        FieldPanel('cnx_description'),
        FieldPanel('allies_heading'),
        FieldPanel('allies_description'),
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


class AboutUsFunders(Orderable, Funders):
    page = ParentalKey('pages.AboutUs', related_name='funders')

class AboutUsStrategicAdvisors(Orderable, StrategicAdvisors):
    page = ParentalKey('pages.AboutUs', related_name='strategic_advisors')   
class AboutUsOpenStaxTeam(Orderable, OpenStaxTeam):
    page = ParentalKey('pages.AboutUs', related_name='openstax_team')   

class AboutUs(Page):
    who_we_are = RichTextField()
    funder_intro = RichTextField()
    strategic_advisors_intro = RichTextField()
    openstax_team_intro = RichTextField()
    api_fields = (
        'who_we_are', 
        'funder_intro', 
        'funders', 
        'strategic_advisors_intro',
        'strategic_advisors',
        'openstax_team_intro',
        'openstax_team'
        'slug',
        'seo_title',
        'search_description',)
    
    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('who_we_are'),
        FieldPanel('funder_intro'),
        InlinePanel('funders', label="Funders"),
        FieldPanel('strategic_advisors_intro'),
        InlinePanel('strategic_advisors', label="Strategic Advisors"),
        FieldPanel('openstax_team_intro'),
        InlinePanel('openstax_team', label="OpenStax Team"),
    ]
    
    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        
    ]
    
    parent_page_types = ['pages.HomePage']


class GeneralPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
    ])
    
    api_fields = (
        'title',
        'body',
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

class Give(Page):
    touchnet_form = RawHTMLBlock()

    content_panels = [
        FieldPanel('title', classname="full title"),
        #FieldPanel('touchnet_form'),
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


#class GeneralHTMLPage(Page): #this will be used for confirmations/forms from sales force, these won't be editable
