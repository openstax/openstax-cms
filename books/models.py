from django.db import models

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey


class Quotes(models.Model):
    quote_text = RichTextField()
    quote_author = models.CharField(max_length=255)
    quote_author_school = models.CharField(max_length=255)
    
    api_fields = ('quote_text', 'quote_author', 'quote_author_school', )
    
    panels = [
        FieldPanel('quote_text'),
        FieldPanel('quote_author'),
        FieldPanel('quote_author_school'),
    ]


class Allies(models.Model):
    ALLY_CATEGORY = (
        ('OH', 'Online Homework'),
        ('AC', 'Adaptive Courseware'),
        ('CT', 'Customized Tools'),
    )
    ally_category = models.CharField(max_length=2,
                        choices=ALLY_CATEGORY)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    heading = models.CharField(max_length=255) 
    description = RichTextField()
    link_url = models.URLField(blank=True, help_text="Call to Action Link")
    link_text = models.CharField(max_length=255, help_text="Call to Action Text")
    
    api_fields = ('ally_category', 'logo', 'heading', 'description', 'link_url', 'link_text', )
    
    panels = [
        FieldPanel('ally_category'),
        ImageChooserPanel('logo'),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('link_url'),
        FieldPanel('link_text'),
    ]


class StudentResources(models.Model):
    heading = models.CharField(max_length=255) 
    description = RichTextField()
    
    api_fields = ('heading', 'description', )
    
    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
    ]


class FacultyResources(models.Model):
    heading = models.CharField(max_length=255) 
    description = RichTextField()
    
    api_fields = ('heading', 'description', )
    
    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
    ]
    

class Authors(models.Model):
    name = models.CharField(max_length=255) 
    university = models.CharField(max_length=255) 
    country = models.CharField(max_length=255) 
    senior_author = models.BooleanField()
    
    api_fields = ('name', 'university', 'country', 'senior_author', )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('university'),
        FieldPanel('country'),
        FieldPanel('senior_author'),
    ]
    

class BookQuotes(Orderable, Quotes):
    ally = ParentalKey('books.Book', related_name='book_quotes')
    

class BookAllies(Orderable, Allies):
    ally = ParentalKey('books.Book', related_name='book_allies')


class BookStudentResources(Orderable, StudentResources):
    resource = ParentalKey('books.Book', related_name='book_student_resources')  


class BookFacultyResources(Orderable, FacultyResources):
    resource = ParentalKey('books.Book', related_name='book_faculty_resources')


class ContributingAuthors(Orderable, Authors):
    resource = ParentalKey('books.Book', related_name='book_contributing_authors')
              
    
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
        InlinePanel('book_quotes', label="Quotes"),
        InlinePanel('book_allies', label="Allies"),
        InlinePanel('book_student_resources', label="Student Resources"),
        InlinePanel('book_faculty_resources', label="Faculty Resources"),
        InlinePanel('book_contributing_authors', label="Contributing Authors"),
        FieldPanel('publish_date'),
        FieldPanel('isbn_10'),
        FieldPanel('isbn_13'),
    ]
    
    api_fields = ('created',
                  'updated',
                  'revision',
                  'description',
                  'cover_image',
                  'book_quotes',
                  'book_allies',
                  'book_student_resources',
                  'book_faculty_resources',
                  'book_contributing_authors',
                  'publish_date',
                  'isbn_10',
                  'isbn_13')

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
    subject_list_heading = models.CharField(max_length=255, blank=True, null=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('page_description'),
        FieldPanel('dev_standards_heading'),
        FieldPanel('dev_standard_1_heading'),
        FieldPanel('dev_standard_1_description'),
        FieldPanel('dev_standard_2_heading'),
        FieldPanel('dev_standard_2_description'),
        FieldPanel('dev_standard_3_heading'),
        FieldPanel('dev_standard_3_description'),
        FieldPanel('subject_list_heading'),
    ]
    
    api_fields = (
        'title',
        'page_description',
        'dev_standards_heading',
        'dev_standard_1_heading',
        'dev_standard_1_description',
        'dev_standard_2_heading',
        'dev_standard_2_description',
        'dev_standard_3_heading',
        'dev_standard_3_description',
        'subject_list_heading',
    )
    
    parent_page_types = ['pages.HomePage']
    subpage_types = ['books.Book']