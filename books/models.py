import re
import html
import json
import urllib
import ssl

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.forms import ValidationError
from django.utils.html import format_html, mark_safe
from django.contrib.postgres.fields import ArrayField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (FieldPanel,
                                         InlinePanel,
                                         PageChooserPanel,
                                         StreamFieldPanel)
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.admin.edit_handlers import TabbedInterface, ObjectList
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.core.models import Site

from openstax.functions import build_document_url, build_image_url
from snippets.models import FacultyResource, StudentResource, Subject, SharedContent


def cleanhtml(raw_html):
    remove_numbers = re.sub('<span class=\W*(os-number)\W*>.*?>', '', raw_html)
    remove_dividers = re.sub('<span class=\W*(os-divider)\W*>.*?>', '', remove_numbers)
    cleanr = re.compile('<.*?>')
    cleantext = html.unescape(re.sub(cleanr, '', remove_dividers))
    return cleantext


class VideoFacultyResource(models.Model):
    resource_heading = models.CharField(max_length=255)
    resource_description = RichTextField(blank=True, null=True)
    video_title = models.CharField(max_length=255, blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='resource_videos', blank=True, null=True)

    api_fields = [
        APIField('resource_heading'),
        APIField('resource_description'),
        APIField('video_title'),
        APIField('video_url'),
        APIField('video_file'),
    ]

    panels = [
        FieldPanel('resource_heading'),
        FieldPanel('resource_description'),
        FieldPanel('video_title'),
        FieldPanel('video_url'),
        FieldPanel('video_file'),
    ]

class OrientationFacultyResource(models.Model):
    resource_heading = models.CharField(max_length=255, null=True)
    resource_description = RichTextField(blank=True, null=True)
    resource_unlocked = models.BooleanField(default=False)
    creator_fest_resource = models.BooleanField(default=False)

    link_external = models.URLField("External link", blank=True,
                                    help_text="Provide an external URL starting with https:// (or fill out either one of the following two).")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Or select an existing page to attach."
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Or select a document for viewers to download."
    )

    def get_link_document(self):
        return build_document_url(self.link_document.url)

    link_document_url = property(get_link_document)

    def get_document_title(self):
        return self.link_document.title

    link_document_title = property(get_document_title)

    link_text = models.CharField(max_length=255, help_text="Call to Action Text")
    video_reference_number = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date resource was updated')
    featured = models.BooleanField(default=False, help_text="Add to featured bar on resource page")

    api_fields = [
        APIField('resource_heading'),
        APIField('resource_description'),
        APIField('resource_unlocked'),
        APIField('creator_fest_resource'),
        APIField('link_external'),
        APIField('link_page'),
        APIField('link_document_url'),
        APIField('link_document_title'),
        APIField('link_text'),
        APIField('video_reference_number'),
        APIField('updated'),
        APIField('featured'),
    ]

    panels = [
        FieldPanel('resource_heading'),
        FieldPanel('resource_description'),
        FieldPanel('resource_unlocked'),
        FieldPanel('creator_fest_resource'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_text'),
        FieldPanel('video_reference_number'),
        FieldPanel('updated'),
        FieldPanel('featured'),
    ]

class FacultyResources(models.Model):
    resource = models.ForeignKey(
        FacultyResource,
        null=True,
        help_text="Manage resources through snippets.",
        related_name='+',
        on_delete=models.SET_NULL
    )

    def get_resource_heading(self):
        return self.resource.heading
    resource_heading = property(get_resource_heading)

    def get_resource_description(self):
        return self.resource.description
    resource_description = property(get_resource_description)

    def get_resource_unlocked(self):
        return self.resource.unlocked_resource
    resource_unlocked = property(get_resource_unlocked)

    def get_resource_creator_fest_resource(self):
        return self.resource.creator_fest_resource
    creator_fest_resource = property(get_resource_creator_fest_resource)

    link_external = models.URLField("External link", blank=True, help_text="Provide an external URL starting with https:// (or fill out either one of the following two).")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Or select an existing page to attach."
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Or select a document for viewers to download."
    )

    def get_link_document(self):
        return build_document_url(self.link_document.url)
    link_document_url = property(get_link_document)

    def get_document_title(self):
        return self.link_document.title
    link_document_title = property(get_document_title)

    link_text = models.CharField(max_length=255, help_text="Call to Action Text")
    coming_soon_text = models.CharField(max_length=255, null=True, blank=True, help_text="If there is text in this field a coming soon banner will be added with this description.")
    video_reference_number = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date resource was updated')
    featured = models.BooleanField(default=False, help_text="Add to featured bar on resource page")
    k12 = models.BooleanField(default=False, help_text="Add K12 banner to resource")
    print_link = models.URLField(blank=True, null=True, help_text="Link for Buy Print link on resource")

    api_fields = [
        APIField('resource_heading'),
        APIField('resource_description'),
        APIField('resource_unlocked'),
        APIField('creator_fest_resource'),
        APIField('link_external'),
        APIField('link_page'),
        APIField('link_document_url'),
        APIField('link_document_title'),
        APIField('link_text'),
        APIField('coming_soon_text'),
        APIField('video_reference_number'),
        APIField('updated'),
        APIField('featured'),
        APIField('k12'),
        APIField('print_link')
    ]

    panels = [
        SnippetChooserPanel('resource'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_text'),
        FieldPanel('coming_soon_text'),
        FieldPanel('video_reference_number'),
        FieldPanel('updated'),
        FieldPanel('featured'),
        FieldPanel('k12'),
        FieldPanel('print_link')
    ]

    def clean(self):
        errors = {}
        external = self.link_external
        page = self.link_page
        document = self.link_document
        if not external and not page and not document:
            errors.setdefault('link_external', []).append('One of these fields must be populated: External link, Link page or Link document.')

        if errors:
            raise ValidationError(errors)


class StudentResources(models.Model):
    resource = models.ForeignKey(
        StudentResource,
        null=True,
        help_text="Manage resources through snippets.",
        related_name='+',
        on_delete=models.SET_NULL
    )

    def get_resource_heading(self):
        return self.resource.heading
    resource_heading = property(get_resource_heading)

    def get_resource_description(self):
        return self.resource.description
    resource_description = property(get_resource_description)

    def get_resource_unlocked(self):
        return self.resource.unlocked_resource
    resource_unlocked = property(get_resource_unlocked)

    link_external = models.URLField("External link", blank=True, help_text="Provide an external URL starting with http:// (or fill out either one of the following two).")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Or select an existing page to attach."
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Or select a document for viewers to download."
    )

    def get_link_document(self):
        return build_document_url(self.link_document.url)
    link_document_url = property(get_link_document)

    def get_document_title(self):
        return self.link_document.title
    link_document_title = property(get_document_title)

    link_text = models.CharField(max_length=255, help_text="Call to Action Text")
    coming_soon_text = models.CharField(max_length=255, null=True, blank=True, help_text="If there is text in this field a coming soon banner will be added with this description.")
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date resource was updated')
    print_link = models.URLField(blank=True, null=True, help_text="Link for Buy Print link on resource")

    api_fields = [
        APIField('resource_heading'),
        APIField('resource_description'),
        APIField('resource_unlocked'),
        APIField('link_external'),
        APIField('link_page'),
        APIField('link_document_url'),
        APIField('link_document_title'),
        APIField('link_text'),
        APIField('coming_soon_text'),
        APIField('updated'),
        APIField('print_link')
    ]

    panels = [
        SnippetChooserPanel('resource'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_text'),
        FieldPanel('coming_soon_text'),
        FieldPanel('updated'),
        FieldPanel('print_link')
    ]

    def clean(self):
        errors = {}
        external = self.link_external
        page = self.link_page
        document = self.link_document
        if not external and not page and not document:
            errors.setdefault('link_external', []).append('One of these fields must be populated: External link, Link page or Link document.')

        if errors:
            raise ValidationError(errors)


class Authors(models.Model):
    name = models.CharField(max_length=255, help_text="Full name of the author.")
    university = models.CharField(max_length=255, null=True, blank=True, help_text="Name of the university/institution the author is associated with.")
    country = models.CharField(max_length=255, null=True, blank=True, help_text="Country of the university/institution.")
    senior_author = models.BooleanField(default=False, help_text="Whether the author is a senior author. (Senior authors are shown before non-senior authors.)")
    display_at_top = models.BooleanField(default=False, help_text="Whether display the author on top.")
    book = ParentalKey(
        'books.Book', related_name='book_contributing_authors', null=True, blank=True)

    api_fields = [
        APIField('name'),
        APIField('university'),
        APIField('country'),
        APIField('senior_author'),
        APIField('display_at_top'),
    ]

    panels = [
        FieldPanel('name'),
        FieldPanel('university'),
        FieldPanel('country'),
        FieldPanel('senior_author'),
        FieldPanel('display_at_top'),
    ]


class AuthorBlock(blocks.StructBlock):
        name = blocks.CharBlock(required=True, help_text="Full name of the author.")
        university = blocks.CharBlock(required=False, help_text="Name of the university/institution the author is associated with.")
        country = blocks.CharBlock(required=False, help_text="Country of the university/institution.")
        senior_author = blocks.BooleanBlock(required=False, help_text="Whether the author is a senior author. (Senior authors are shown before non-senior authors.)")
        display_at_top = blocks.BooleanBlock(required=False, help_text="Whether display the author on top.")

        class Meta:
            icon = 'user'


class SubjectBooks(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='subjects_subject')

    def get_subject_name(self):
        return self.subject.name
    subject_name = property(get_subject_name)

    def get_subject_page_content(self):
        return self.subject.page_content
    subject_page_content = property(get_subject_page_content)

    def get_subject_page_title(self):
        return self.subject.seo_title
    subject_seo_title = property(get_subject_page_title)

    def get_subject_meta(self):
        return self.subject.search_description
    subject_search_description = property(get_subject_meta)

    api_fields = [
        APIField('subject_name'),
        APIField('subject_page_content'),
        APIField('subject_search_description')
    ]


class SharedContentChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'heading': value.heading,
                'content': value.content,
                'content_logged_in': value.content_logged_in,
                'button_text': value.button_text,
                'button_url': value.button_url,
            }


class SharedContentBlock(blocks.StreamBlock):
    content = SharedContentChooserBlock(SharedContent)
    link = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=False)

    class Meta:
        icon = 'document'
        required = False


class BookFacultyResources(Orderable, FacultyResources):
    book_faculty_resource = ParentalKey('books.Book', related_name='book_faculty_resources')


class VideoFacultyResources(Orderable, VideoFacultyResource):
    book_video_faculty_resource = ParentalKey('books.Book', related_name='book_video_faculty_resources')

class OrientationFacultyResources(Orderable, OrientationFacultyResource):
    book_orientation_faculty_resource = ParentalKey('books.Book', related_name='book_orientation_faculty_resources')

class BookStudentResources(Orderable, StudentResources):
    book_student_resource = ParentalKey('books.Book', related_name='book_student_resources')


class BookSubjects(Orderable, SubjectBooks):
    book_subject = ParentalKey('books.Book', related_name='book_subjects')


BLUE = 'blue'
DEEP_GREEN = 'deep-green'
GOLD = 'gold'
GRAY = 'gray'
GREEN = 'green'
LIGHT_BLUE = 'light-blue'
LIGHT_GRAY = 'light-gray'
MEDIUM_BLUE = 'medium-blue'
ORANGE = 'orange'
RED = 'red'
YELLOW = 'yellow'
COVER_COLORS = (
    (BLUE, 'Blue'),
    (DEEP_GREEN, 'Deep Green'),
    (GOLD, 'Gold'),
    (GRAY, 'Gray'),
    (GREEN, 'Green'),
    (LIGHT_BLUE, 'Light Blue'),
    (LIGHT_GRAY, 'Light Gray'),
    (MEDIUM_BLUE, 'Medium Blue'),
    (ORANGE, 'Orange'),
    (RED, 'Red'),
    (YELLOW, 'Yellow'),
)

YELLOW = 'yellow'
LIGHT_BLUE = 'light_blue'
DARK_BLUE = 'dark_blue'
GREEN = 'green'
WHITE = 'white'
GREY = 'grey'
RED = 'red'
WHITE_RED = 'white_red'
WHITE_BLUE = 'white_blue'
GREEN_WHITE = 'green_white'
YELLOW_WHITE = 'yellow_white'
GREY_WHITE = 'grey_white'
WHITE_GREY = 'white_grey'
WHITE_ORANGE = 'white_orange'
BOOK_COVER_TEXT_COLOR = (
    (YELLOW, 'Yellow'),
    (LIGHT_BLUE, 'Light Blue'),
    (DARK_BLUE, 'Dark Blue'),
    (GREEN, 'Green'),
    (WHITE, 'White'),
    (GREY, 'Grey'),
    (RED, 'Red'),
    (WHITE_RED, 'White/Red'),
    (WHITE_BLUE, 'White/Blue'),
    (GREEN_WHITE, 'Green/White'),
    (YELLOW_WHITE, 'Yellow/White'),
    (GREY_WHITE, 'Grey/White'),
    (WHITE_GREY, 'White/Grey'),
    (WHITE_ORANGE, 'White/Orange'),
)

LIVE = 'live'
COMING_SOON = 'coming_soon'
NEW_EDITION_AVAILABLE = 'new_edition_available'
DEPRECATED = 'deprecated'
RETIRED = 'retired'
BOOK_STATES = (
    (LIVE, 'Live'),
    (COMING_SOON, 'Coming Soon'),
    (NEW_EDITION_AVAILABLE, 'New Edition Forthcoming (Show new edition correction schedule)'),
    (DEPRECATED, 'Deprecated (Disallow errata submissions and show deprecated schedule)'),
    (RETIRED, 'Retired (Remove from website)')
)


class Book(Page):
    created = models.DateTimeField(auto_now_add=True)
    book_state = models.CharField(max_length=255, choices=BOOK_STATES, default='live', help_text='The state of the book.')
    cnx_id = models.CharField(
        max_length=255, help_text="This is used to pull relevant information from CNX.",
        blank=True, null=True)
    salesforce_abbreviation = models.CharField(max_length=255, blank=True, null=True, verbose_name='Internal Salesforce Name')
    salesforce_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Website Visible Salesforce Name')
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date web content was updated')
    is_ap = models.BooleanField(default=False, help_text='Whether this book is an AP (Advanced Placement) book.')
    description = RichTextField(
        blank=True, help_text="Description shown on Book Detail page.")

    cover = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The book cover to be shown on the website.'
    )
    def get_cover_url(self):
        return build_document_url(self.cover.url)
    cover_url = property(get_cover_url)

    title_image = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The svg for title image to be shown on the website.'
    )
    def get_title_image_url(self):
        return build_document_url(self.title_image.url)
    title_image_url = property(get_title_image_url)

    cover_color = models.CharField(max_length=255, choices=COVER_COLORS, default='blue', help_text='The color of the cover.')
    book_cover_text_color = models.CharField(max_length=255, choices=BOOK_COVER_TEXT_COLOR, default='yellow', help_text="Use by the Unified team - this will not change the text color on the book cover.")
    reverse_gradient = models.BooleanField(default=False)
    publish_date = models.DateField(null=True, help_text='Date the book is published on.')
    authors = StreamField([
        ('author', AuthorBlock()),
    ], null=True)

    print_isbn_10 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 10 for print version (hardcover).')
    print_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for print version (hardcover).')
    print_softcover_isbn_10 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 10 for print version (softcover).')
    print_softcover_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for print version (softcover).')
    digital_isbn_10 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 10 for digital version.')
    digital_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for digital version.')
    ibook_isbn_10 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 10 for iBook version.')
    ibook_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for iBook version.')
    ibook_volume_2_isbn_10 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 10 for iBook v2 version.')
    ibook_volume_2_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for iBook v2 version.')
    license_text = models.TextField(
        blank=True, null=True, help_text="Overrides default license text.")
    license_name = models.CharField(
        max_length=255, blank=True, null=True, editable=False, help_text="Name of the license.")
    license_version = models.CharField(
        max_length=255, blank=True, null=True, editable=False, help_text="Version of the license.")
    license_url = models.CharField(
        max_length=255, blank=True, null=True, editable=False, help_text="External URL of the license.")

    high_resolution_pdf = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="High quality PDF document of the book."
    )
    def get_high_res_pdf_url(self):
        if self.high_resolution_pdf:
            return build_document_url(self.high_resolution_pdf.url)
        else:
            return None
    high_resolution_pdf_url = property(get_high_res_pdf_url)

    low_resolution_pdf = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Low quality PDF document of the book."
    )
    def get_low_res_pdf_url(self):
        if self.low_resolution_pdf:
            return build_document_url(self.low_resolution_pdf.url)
        else:
            return None
    low_resolution_pdf_url = property(get_low_res_pdf_url)

    free_stuff_instructor = StreamField(SharedContentBlock(), null=True, blank=True, help_text="Snippet to show texts for free instructor resources.")
    free_stuff_student = StreamField(SharedContentBlock(), null=True, blank=True, help_text="Snipped to show texts for free student resources.")
    community_resource_heading = models.CharField(max_length=255, blank=True, null=True, help_text="Snipped to show texts for community resources.")
    community_resource_logo = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Logo for community resources."
    )

    def get_community_resource_logo_url(self):
        if self.community_resource_logo:
            return build_document_url(self.community_resource_logo.url)
        else:
            return None

    community_resource_logo_url = property(get_community_resource_logo_url)
    community_resource_cta = models.CharField(max_length=255, blank=True, null=True, help_text='Call the action text.')
    community_resource_url = models.URLField(blank=True, help_text='URL of the external source.')
    community_resource_blurb = models.TextField(blank=True, help_text='Blurb.')
    community_resource_feature_link = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text='Document of the community resource feature.'
    )
    def get_community_resource_feature_link_url(self):
        return build_document_url(self.community_resource_feature_link.url)

    community_resource_feature_link_url = property(get_community_resource_feature_link_url)
    community_resource_feature_text = models.TextField(blank=True, help_text='Text of the community resource feature.')


    webinar_content = StreamField(SharedContentBlock(), null=True, blank=True)
    ibook_link = models.URLField(blank=True, help_text="Link to iBook")
    ibook_link_volume_2 = models.URLField(blank=True, help_text="Link to secondary iBook")
    webview_link = models.URLField(blank=True, help_text="Link to CNX Webview book")
    webview_rex_link = models.URLField(blank=True, help_text="Link to REX Webview book")
    rex_callout_title = models.CharField(max_length=255, blank=True, null=True, help_text='Title of the REX callout', default="Recommended")
    rex_callout_blurb = models.CharField(max_length=255, blank=True, null=True, help_text='Additional text for the REX callout.')
    enable_study_edge = models.BooleanField(default=False, help_text="This will cause the link to the Study Edge app appear on the book details page.")
    bookshare_link = models.URLField(blank=True, help_text="Link to Bookshare resources")
    amazon_coming_soon = models.BooleanField(default=False, verbose_name="Individual Print Coming Soon")
    amazon_link = models.URLField(blank=True, verbose_name="Individual Print Link")
    kindle_link = models.URLField(blank=True, help_text="Link to Kindle version")
    chegg_link = models.URLField(blank=True, null=True, help_text="Link to Chegg e-reader")
    chegg_link_text = models.CharField(max_length=255, blank=True, null=True, help_text='Text for Chegg link.')
    bookstore_coming_soon = models.BooleanField(default=False, help_text='Whether this book is coming to bookstore soon.')
    bookstore_content = StreamField(SharedContentBlock(), null=True, blank=True, help_text='Bookstore content.')
    comp_copy_available = models.BooleanField(default=True, help_text='Whether free compy available for teachers.')
    comp_copy_content = StreamField(SharedContentBlock(), null=True, blank=True, help_text='Content of the free copy.')
    errata_content = StreamField(SharedContentBlock(), null=True, blank=True, help_text='Errata content.')
    tutor_marketing_book = models.BooleanField(default=False, help_text='Whether this is a Tutor marketing book.')
    partner_list_label = models.CharField(max_length=255, null=True, blank=True, help_text="Controls the heading text on the book detail page for partners. This will update ALL books to use this value!")
    partner_page_link_text = models.CharField(max_length=255, null=True, blank=True, help_text="Link to partners page on top right of list.")
    featured_resources_header = models.CharField(max_length=255, null=True, blank=True, help_text="Featured resource header on instructor resources tab.")

    customization_form_heading = models.CharField(max_length=255, null=True, blank=True, help_text="Heading for the CE customization form. This will update ALL books to use this value!", default="Customization Form")
    customization_form_subheading = models.CharField(max_length=255, null=True, blank=True, help_text="Subheading for the CE customization form. This will update ALL books to use this value!", default="Please select the modules (up to 10), that you want to customize with Google Docs.")
    customization_form_disclaimer = RichTextField(blank=True, help_text="This will update ALL books to use this value!", default="<p><b>Disclaimer</b></p><p>The following features and functionality are not available to teachers and students using Google Docs customized content:</p><ul><li><b>Errata updates</b>. OpenStax webview is updated at least twice yearly. Customized Google Docs will not receive these content updates.</li><li><b>Access to study tools</b>. OpenStax webview has in-book search, highlighting, study guides, and more available for free. This functionality will not be available in Google Docs versions.</li><li><b>Formatting. </b>Print books and webview have a specific design and structure format developed for those platforms. These functionalities are not available in the Google Docs versions.</li></ul>")
    customization_form_next_steps = RichTextField(blank=True, help_text="This will update ALL books to use this value!", default="<p><b>Next Steps</b></p><ol><li>Within two business days, you will receive an email for each module that you have requested access to customize.</li><li>The link provided in the email will be your own copy of the Google Doc that OpenStax generated for you.</li><li>Once you have accessessed the document you can make the changes you desire and share with your students. We recommend using the &quot;Publish to the Web&quot; functionality under the file menu for sharing with students.</li></ol>")
    adoptions = models.IntegerField(blank=True, null=True)
    savings = models.IntegerField(blank=True, null=True)
    support_statement = models.TextField(blank=True, null=True, default="With philanthropic support, this book is used in <span id='adoption_number'></span> classrooms, saving students <span id='savings'></span> dollars this school year. <a href='/impact'>Learn more about our impact</a> and how you can help.", help_text="Updating this statement updates it for all book pages.")


    videos = StreamField([
        ('video', blocks.ListBlock(blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('description', blocks.RichTextBlock()),
            ('embed', blocks.RawHTMLBlock()),
        ])))
    ], null=True, blank=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Promote image.'
    )

    last_updated_pdf = models.DateTimeField(blank=True, null=True, help_text="Last time PDF was revised.", verbose_name='PDF Content Revision Date')

    book_detail_panel = Page.content_panels + [
        FieldPanel('book_state'),
        FieldPanel('cnx_id'),
        FieldPanel('salesforce_abbreviation'),
        FieldPanel('salesforce_name'),
        FieldPanel('updated'),
        FieldPanel('publish_date'),
        InlinePanel('book_subjects', label='Subjects'),
        FieldPanel('is_ap'),
        FieldPanel('description', classname="full"),
        DocumentChooserPanel('cover'),
        DocumentChooserPanel('title_image'),
        FieldPanel('cover_color'),
        FieldPanel('book_cover_text_color'),
        FieldPanel('reverse_gradient'),
        FieldPanel('print_isbn_10'),
        FieldPanel('print_isbn_13'),
        FieldPanel('print_softcover_isbn_10'),
        FieldPanel('print_softcover_isbn_13'),
        FieldPanel('digital_isbn_10'),
        FieldPanel('digital_isbn_13'),
        FieldPanel('ibook_isbn_10'),
        FieldPanel('ibook_isbn_13'),
        FieldPanel('ibook_volume_2_isbn_10'),
        FieldPanel('ibook_volume_2_isbn_13'),
        FieldPanel('license_text'),
        FieldPanel('webview_rex_link'),
        FieldPanel('rex_callout_title'),
        FieldPanel('rex_callout_blurb'),
        FieldPanel('enable_study_edge'),
        DocumentChooserPanel('high_resolution_pdf'),
        FieldPanel('last_updated_pdf'),
        DocumentChooserPanel('low_resolution_pdf'),
        StreamFieldPanel('free_stuff_instructor'),
        StreamFieldPanel('free_stuff_student'),
        FieldPanel('community_resource_heading'),
        DocumentChooserPanel('community_resource_logo'),
        FieldPanel('community_resource_url'),
        FieldPanel('community_resource_cta'),
        FieldPanel('community_resource_blurb'),
        DocumentChooserPanel('community_resource_feature_link'),
        FieldPanel('community_resource_feature_text'),
        StreamFieldPanel('webinar_content'),
        FieldPanel('ibook_link'),
        FieldPanel('ibook_link_volume_2'),
        FieldPanel('bookshare_link'),
        FieldPanel('amazon_coming_soon'),
        FieldPanel('amazon_link'),
        FieldPanel('kindle_link'),
        FieldPanel('chegg_link'),
        FieldPanel('chegg_link_text'),
        FieldPanel('bookstore_coming_soon'),
        StreamFieldPanel('bookstore_content'),
        FieldPanel('comp_copy_available'),
        StreamFieldPanel('comp_copy_content'),
        StreamFieldPanel('errata_content'),
        FieldPanel('tutor_marketing_book'),
        FieldPanel('partner_list_label'),
        FieldPanel('partner_page_link_text'),
        FieldPanel('customization_form_heading'),
        FieldPanel('customization_form_subheading'),
        FieldPanel('customization_form_disclaimer'),
        FieldPanel('customization_form_next_steps'),
        FieldPanel('support_statement'),
        StreamFieldPanel('videos'),
    ]
    instructor_resources_panel = [
        FieldPanel('featured_resources_header'),
        InlinePanel('book_video_faculty_resources', label='Video Resource', max_num=1),
        InlinePanel('book_orientation_faculty_resources', label='Instruction Orientation Resource', max_num=1),
        InlinePanel('book_faculty_resources', label="Instructor Resources"),
    ]
    student_resources_panel = [
        InlinePanel('book_student_resources', label="Student Resources"),
    ]
    author_panel = [
        StreamFieldPanel('authors')
    ]
    promote_panels = Page.promote_panels + [
        ImageChooserPanel('promote_image'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(book_detail_panel, heading='Book Details'),
        ObjectList(instructor_resources_panel, heading='Instructor Resources'),
        ObjectList(student_resources_panel, heading='Student Resources'),
        ObjectList(author_panel, heading='Authors'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
    ])

    api_fields = [
        APIField('created'),
        APIField('updated'),
        APIField('slug'),
        APIField('title'),
        APIField('book_state'),
        APIField('cnx_id'),
        APIField('salesforce_abbreviation'),
        APIField('salesforce_name'),
        APIField('book_subjects'),
        APIField('is_ap'),
        APIField('description'),
        APIField('cover_url'),
        APIField('title_image_url'),
        APIField('cover_color'),
        APIField('book_cover_text_color'),
        APIField('reverse_gradient'),
        APIField('book_student_resources'),
        APIField('book_video_faculty_resources'),
        APIField('book_orientation_faculty_resources'),
        APIField('book_faculty_resources'),
        APIField('publish_date'),
        APIField('authors'),
        APIField('print_isbn_10'),
        APIField('print_isbn_13'),
        APIField('print_softcover_isbn_10'),
        APIField('print_softcover_isbn_13'),
        APIField('digital_isbn_10'),
        APIField('digital_isbn_13'),
        APIField('ibook_isbn_10'),
        APIField('ibook_isbn_13'),
        APIField('ibook_volume_2_isbn_10'),
        APIField('ibook_volume_2_isbn_13'),
        APIField('license_text'),
        APIField('license_name'),
        APIField('license_version'),
        APIField('license_url'),
        APIField('high_resolution_pdf_url'),
        APIField('low_resolution_pdf_url'),
        APIField('free_stuff_instructor'),
        APIField('free_stuff_student'),
        APIField('community_resource_heading'),
        APIField('community_resource_logo_url'),
        APIField('community_resource_url'),
        APIField('community_resource_cta'),
        APIField('community_resource_blurb'),
        APIField('community_resource_feature_link_url'),
        APIField('community_resource_feature_text'),
        APIField('webinar_content'),
        APIField('ibook_link'),
        APIField('ibook_link_volume_2'),
        APIField('webview_link'),
        APIField('webview_rex_link'),
        APIField('rex_callout_title'),
        APIField('rex_callout_blurb'),
        APIField('enable_study_edge'),
        APIField('bookshare_link'),
        APIField('amazon_coming_soon'),
        APIField('amazon_link'),
        APIField('kindle_link'),
        APIField('chegg_link'),
        APIField('chegg_link_text'),
        APIField('bookstore_coming_soon'),
        APIField('bookstore_content'),
        APIField('comp_copy_available'),
        APIField('comp_copy_content'),
        APIField('errata_content'),
        APIField('tutor_marketing_book'),
        APIField('partner_list_label'),
        APIField('partner_page_link_text'),
        APIField('customization_form_heading'),
        APIField('customization_form_subheading'),
        APIField('customization_form_disclaimer'),
        APIField('customization_form_next_steps'),
        APIField('videos'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
        APIField('last_updated_pdf'),
        APIField('featured_resources_header'),
        APIField('support_statement'),
        APIField('adoptions'),
        APIField('savings')
    ]

    template = 'page.html'

    parent_page_types = ['books.BookIndex']

    @property
    def book_title(self):
        return format_html(
            '{}',
            mark_safe(self.book.title),
        )

    def subjects(self):
        subject_list = []
        for subject in self.book_subjects.all():
            subject_list.append(subject.subject_name)
        return subject_list

    def get_slug(self):
        return 'books/{}'.format(self.slug)

    def book_urls(self):
        book_urls = []
        for field in self.api_fields:
            try:
                url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', getattr(self, field))
                if url:
                    book_urls.append(url)
            except(TypeError, AttributeError):
                pass
        return book_urls


    def save(self, *args, **kwargs):
        if self.cnx_id:
            self.webview_link = '{}contents/{}'.format(settings.CNX_URL, self.cnx_id)

        if self.partner_list_label:
            Book.objects.all().update(partner_list_label=self.partner_list_label)

        if self.partner_page_link_text:
            Book.objects.all().update(partner_page_link_text=self.partner_page_link_text)

        # sync customization form changes on all books
        if self.customization_form_heading:
            Book.objects.all().update(customization_form_heading=self.customization_form_heading)
        if self.customization_form_subheading:
            Book.objects.all().update(customization_form_subheading=self.customization_form_subheading)
        if self.customization_form_disclaimer:
            Book.objects.all().update(customization_form_disclaimer=self.customization_form_disclaimer)
        if self.customization_form_next_steps:
            Book.objects.all().update(customization_form_next_steps=self.customization_form_next_steps)
        if self.support_statement:
            Book.objects.all().update(support_statement=self.support_statement)

        return super(Book, self).save(*args, **kwargs)


    def get_url_parts(self, *args, **kwargs):
        # This overrides the "Live" link in admin to take you to proper FE page
        url_parts = super(Book, self).get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, root_url, page_path = url_parts
        page_path = '/details/books/' + self.slug

        return (site_id, root_url, page_path)


    def get_sitemap_urls(self, request=None):
        return [
            {
                'location': '{}/details/books/{}'.format(Site.find_for_request(request).root_url, self.slug),
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]

    def __str__(self):
        return self.book_title


class BookIndex(Page):
    page_description = models.TextField()
    dev_standards_heading = models.CharField(
        max_length=255, blank=True, null=True)
    dev_standard_1_heading = models.CharField(
        max_length=255, blank=True, null=True)
    dev_standard_1_description = RichTextField()
    dev_standard_2_heading = models.CharField(
        max_length=255, blank=True, null=True)
    dev_standard_2_description = RichTextField()
    dev_standard_3_heading = models.CharField(
        max_length=255, blank=True, null=True)
    dev_standard_3_description = RichTextField()
    dev_standard_4_heading = models.CharField(
        max_length=255, blank=True, null=True)
    dev_standard_4_description = models.TextField(help_text="Keep <span> in place to populate with Salesforce data. id=adoption_number for classrooms and id=savings for savings number.")
    subject_list_heading = models.CharField(
        max_length=255, blank=True, null=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def books(self):
        books = Book.objects.live().order_by('path')
        book_data = []
        for book in books:
            has_faculty_resources = BookFacultyResources.objects.filter(book_faculty_resource=book).exists()
            has_student_resources = BookStudentResources.objects.filter(book_student_resource=book).exists()
            try:
                book_data.append({
                    'id': book.id,
                    'slug': 'books/{}'.format(book.slug),
                    'book_state': book.book_state,
                    'title': book.title,
                    'subjects': book.subjects(),
                    'is_ap': book.is_ap,
                    'cover_url': book.cover_url,
                    'cover_color': book.cover_color,
                    'high_resolution_pdf_url': book.high_resolution_pdf_url,
                    'low_resolution_pdf_url': book.low_resolution_pdf_url,
                    'ibook_link': book.ibook_link,
                    'ibook_link_volume_2': book.ibook_link_volume_2,
                    'webview_link': book.webview_link,
                    'webview_rex_link': book.webview_rex_link,
                    'bookshare_link': book.bookshare_link,
                    'kindle_link': book.kindle_link,
                    'amazon_coming_soon': book.amazon_coming_soon,
                    'amazon_link': book.amazon_link,
                    'bookstore_coming_soon': book.bookstore_coming_soon,
                    'comp_copy_available': book.comp_copy_available,
                    'salesforce_abbreviation': book.salesforce_abbreviation,
                    'salesforce_name': book.salesforce_name,
                    'urls': book.book_urls(),
                    'last_updated_pdf': book.last_updated_pdf,
                    'has_faculty_resources': has_faculty_resources,
                    'has_student_resources': has_student_resources
                })
            except Exception as e:
                print("Error: {}".format(e))
        return book_data

    content_panels = Page.content_panels + [
        FieldPanel('page_description'),
        FieldPanel('dev_standards_heading'),
        FieldPanel('dev_standard_1_heading'),
        FieldPanel('dev_standard_1_description'),
        FieldPanel('dev_standard_2_heading'),
        FieldPanel('dev_standard_2_description'),
        FieldPanel('dev_standard_3_heading'),
        FieldPanel('dev_standard_3_description'),
        FieldPanel('dev_standard_4_heading'),
        FieldPanel('dev_standard_4_description'),
        FieldPanel('subject_list_heading'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    api_fields = [
        APIField('title'),
        APIField('page_description'),
        APIField('dev_standards_heading'),
        APIField('dev_standard_1_heading'),
        APIField('dev_standard_1_description'),
        APIField('dev_standard_2_heading'),
        APIField('dev_standard_2_description'),
        APIField('dev_standard_3_heading'),
        APIField('dev_standard_3_description'),
        APIField('dev_standard_4_heading'),
        APIField('dev_standard_4_description'),
        APIField('subject_list_heading'),
        APIField('books'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage']
    subpage_types = ['books.Book']
    max_count = 1
