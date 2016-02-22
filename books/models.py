import urllib, json, dateutil.parser, requests
from lxml import html

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                PageChooserPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey

from allies.models import Ally


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


class Resource(models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField()

    api_fields = ('heading', 'description', )

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.heading

register_snippet(Resource)


class StudentResources(models.Model):
    resource = models.ForeignKey(
        Resource,
        null=True,
        help_text="Manage resources through snippets.",
        related_name='+'
    )
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
    link_text = models.CharField(max_length=255, help_text="Call to Action Text")

    api_fields = ('resource', 'link_external', 'link_page',
                  'link_document', 'link_text', )

    panels = [
        SnippetChooserPanel('resource', Resource),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_text'),
    ]


class FacultyResources(models.Model):
    resource = models.ForeignKey(
        Resource,
        null=True,
        help_text="Manage resources through snippets.",
        related_name='+'
    )
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
    link_text = models.CharField(max_length=255, help_text="Call to Action Text")

    api_fields = ('resource', 'link_external', 'link_page',
                  'link_document', 'link_text', )

    panels = [
        SnippetChooserPanel('resource', Resource),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_text'),
    ]
    

class Authors(models.Model):
    name = models.CharField(max_length=255) 
    university = models.CharField(max_length=255, null=True, blank=True) 
    country = models.CharField(max_length=255, null=True, blank=True) 
    senior_author = models.BooleanField(default=False)
    display_at_top = models.BooleanField(default=False)
    book = ParentalKey('books.Book', related_name='book_contributing_authors', null=True, blank=True)
    
    api_fields = ('name', 'university', 'country', 'senior_author', 'display_at_top', )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('university'),
        FieldPanel('country'),
        FieldPanel('senior_author'),
        FieldPanel('display_at_top'),
    ]


class BookAlly(models.Model):
    ally = models.ForeignKey(
        Ally,
        null=True,
        help_text="Manage allies through snippets.",
        on_delete=models.SET_NULL,
        related_name='allies_ally'
    )
    book_link_url = models.URLField(blank=True, help_text="Call to Action Link")
    book_link_text = models.CharField(max_length=255, help_text="Call to Action Text")

    api_fields = ('ally', 'book_link_url', 'book_link_text', )

    panels = [
        SnippetChooserPanel('ally'),
        FieldPanel('book_link_url'),
        FieldPanel('book_link_text'),
    ]


class Subject(models.Model):
    name = models.CharField(max_length=255)
    
    api_fields = ('name', )
    
    panels = [
        FieldPanel('name'),
    ]
    
    def __str__(self):
        return self.name
    

register_snippet(Subject)


class BookQuotes(Orderable, Quotes):
    quote = ParentalKey('books.Book', related_name='book_quotes')


class BookStudentResources(Orderable, StudentResources):
    book_student_resource = ParentalKey('books.Book', related_name='book_student_resources')


class BookFacultyResources(Orderable, FacultyResources):
    book_faculty_resource = ParentalKey('books.Book', related_name='book_faculty_resources')


class BookAllies(Orderable, BookAlly):
    book_ally = ParentalKey('books.Book', related_name='book_allies')
              
    
class Book(Page):
    created = models.DateTimeField(auto_now_add=True)
    cnx_id = models.CharField(max_length=255, help_text="This is used to pull relevant information from CNX.")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL,
                                null=True, related_name='+')

    def get_subject_name(self):
        return self.subject.name

    subject_name = property(get_subject_name)
    updated = models.DateTimeField(auto_now=True)
    is_ap = models.BooleanField(default=False)
    short_description = RichTextField(blank=True, help_text="Description shown on Subject page.")
    description = RichTextField(blank=True, help_text="Description shown on Book Detail page.")
    # we have to change this to a document upload to support SVGs - see
    cover = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    publish_date = models.DateField(blank=True, null=True, editable=False)
    isbn_10 = models.IntegerField(blank=True, null=True)
    isbn_13 = models.CharField(max_length=255, blank=True, null=True)
    license_name = models.CharField(max_length=255, blank=True, null=True, editable=False)
    license_version = models.CharField(max_length=255, blank=True, null=True, editable=False)
    license_url = models.CharField(max_length=255, blank=True, null=True, editable=False)

    content_panels = Page.content_panels + [
        FieldPanel('cnx_id'),
        SnippetChooserPanel('subject', Subject),
        FieldPanel('is_ap'),
        FieldPanel('description', classname="full"),
        DocumentChooserPanel('cover'),
        InlinePanel('book_quotes', label="Quotes"),
        InlinePanel('book_allies', label="Allies"),
        InlinePanel('book_student_resources', label="Student Resources"),
        InlinePanel('book_faculty_resources', label="Faculty Resources"),
        InlinePanel('book_contributing_authors', label="Contributing Authors"),
        FieldPanel('isbn_10'),
        FieldPanel('isbn_13'),
    ]
    
    api_fields = ('created',
                  'updated',
                  'title',
                  'cnx_id',
                  'subject_name',
                  'is_ap',
                  'description',
                  'cover',
                  'book_quotes',
                  'book_allies',
                  'book_student_resources',
                  'book_faculty_resources',
                  'book_contributing_authors',
                  'publish_date',
                  'isbn_10',
                  'isbn_13',
                  'license_name',
                  'license_version',
                  'license_url',)

    parent_page_types = ['books.BookIndex']

    # we are overriding the save() method to go to CNX and fetch information with the CNX ID
    def save(self, *args, **kwargs):
        errors = super(Book, self).check(**kwargs)
        
        url = '{}/contents/{}.json'.format(settings.CNX_ARCHIVE_URL, self.cnx_id)
        response = urllib.request.urlopen(url).read()
        result = json.loads(response.decode('utf-8'))
        
        self.license_name = result['license']['name']
        self.license_version = result['license']['version']
        self.license_url = result['license']['url']
        
        #self.publish_date = dateutil.parser.parse(result['created'])
        
        return super(Book, self).save(*args, **kwargs)

        #self.publish_date = dateutil.parser.parse(result['created'])

        # now let's go fetch the authors from the preface
        # try:
        #     preface = result['tree']['contents'][0]
        #     if(preface['title'] == 'Preface'):
        #         url = '{}/contents/{}.html'.format(settings.CNX_ARCHIVE_URL, preface['id'])
        #         page = requests.get(url)
        #         tree = html.fromstring(page.content)
        #         # we need to save the book so we get a PK that we can attach to the authors
        #         super(Book, self).save(*args, **kwargs)
        #         ## FIXME - We need authors! Not h1 titles! For development only!
        #         # classes will be contrib-auth and sr-contrib-auth
        #         # use this to debug - http://videlibri.sourceforge.net/cgi-bin/xidelcgi
        #         titles = tree.xpath('//*[@id="import-auto-id6936523"]/*[not(self::div and @data-type="newline")]//text() | //*[@id="import-auto-id6936523"]/text()')[1:-3]
        #         for title in titles:
        #             author = title.split(',')[0].strip()
        #             try:
        #                 university = title.split(',')[1].strip().replace('*', '')
        #             except IndexError:
        #                 university = None
        #             # this is causing only one author to get created
        #             if author:
        #                 author, created = Authors.objects.get_or_create(name=author, university=university, book=self)
        #
        #             ## do we need to check if author is no longer there and delete them?
        #
        #         raise ValidationError({'cnx_id': _( "A Preface for the CNX ID you entered was not found.")})
        # except KeyError:
        #     # should this just fail silently and allow them to override? If so, CNX ID not required?
        #     raise ValidationError({'cnx_id': _( "The CNX ID you entered does not match a book with a Preface. This is required to parse authors.")})
        #
        # return super(Book, self).save(*args, **kwargs)


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