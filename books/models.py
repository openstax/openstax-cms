from django.db import models

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey

# Create your models here.

class Authors(models.Model):
    name = models.CharField(max_length=255)
        
    api_fields = ('name', )
    
    panels = [
        FieldPanel('name'),
    ]
        

class BookAuthors(Orderable, Authors):
    page = ParentalKey('books.Book', related_name='book_authors')
    
    
class Book(Page):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    revision = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    publish_date = models.DateField(blank=True, null=True)
    isbn_10 = models.IntegerField(blank=True, null=True)
    isbn_13 = models.CharField(max_length=255, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('revision'),
        FieldPanel('description', classname="full"),
        ImageChooserPanel('cover_image'),
        FieldPanel('publish_date'),
        FieldPanel('isbn_10'),
        FieldPanel('isbn_13'),
        InlinePanel('book_authors', label="Authors"),
    ]
    
    api_fields = ('created',
                  'updated',
                  'revision',
                  'description',
                  'cover_image',
                  'publish_date',
                  'isbn_10',
                  'isbn_13',
                  'book_authors',)

    parent_page_types = ['books.BookIndex']


class BookIndex(Page):
    page_description = RichTextField()
    dev_standards_heading = models.CharField(max_length=255, blank=True, null=True)
    dev_standard_1_heading = models.CharField(max_length=255, blank=True, null=True)
    dev_standard_1_description = RichTextField()
    dev_standard_2_heading = models.CharField(max_length=255, blank=True, null=True)
    dev_standard_2_description = RichTextField()
    dev_standard_3_heading = models.CharField(max_length=255, blank=True, null=True)
    dev_standard_3_description = RichTextField()
    
    content_panels = Page.content_panels + [
        FieldPanel('page_description'),
        FieldPanel('dev_standards_heading'),
        FieldPanel('dev_standard_1_heading'),
        FieldPanel('dev_standard_1_description'),
        FieldPanel('dev_standard_2_heading'),
        FieldPanel('dev_standard_2_description'),
        FieldPanel('dev_standard_3_heading'),
        FieldPanel('dev_standard_3_description'),
    ]
    
    api_fields = (
        'page_description',
        'dev_standards_heading',
        'dev_standard_1_heading',
        'dev_standard_1_description',
        'dev_standard_2_heading',
        'dev_standard_2_description',
        'dev_standard_3_heading',
        'dev_standard_3_description',
    )
    
    parent_page_types = ['pages.HomePage']
    subpage_types = ['books.Book']