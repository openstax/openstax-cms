import re
import html
from sentry_sdk import capture_exception

from django.conf import settings
from django.db import models
from django.utils.html import format_html, mark_safe
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (FieldPanel,
                                  InlinePanel,
                                  PageChooserPanel)
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.admin.panels import TabbedInterface, ObjectList
from wagtail.api import APIField
from wagtail.models import Site

from openstax.functions import build_document_url
from books.constants import BOOK_STATES, BOOK_COVER_TEXT_COLOR, COVER_COLORS, CC_NC_SA_LICENSE_NAME, CC_BY_LICENSE_NAME, \
    CC_BY_LICENSE_URL, CC_NC_SA_LICENSE_URL, CC_NC_SA_LICENSE_VERSION, CC_BY_LICENSE_VERSION, K12_CATEGORIES
import snippets.models as snippets


def cleanhtml(raw_html):
    remove_numbers = re.sub('<span class=\\W*(os-number)\\W*>.*?>', '', raw_html)
    remove_dividers = re.sub('<span class=\\W*(os-divider)\\W*>.*?>', '', remove_numbers)
    cleanr = re.compile('<.*?>')
    cleantext = html.unescape(re.sub(cleanr, '', remove_dividers))
    return cleantext


def prefetch_book_resources(queryset):
    """Prefetch related faculty and student resources for a queryset of books."""
    return queryset.prefetch_related(
        models.Prefetch('bookfacultyresources_set', queryset=BookFacultyResources.objects.all(), to_attr='prefetched_faculty_resources'),
        models.Prefetch('bookstudentresources_set', queryset=BookStudentResources.objects.all(), to_attr='prefetched_student_resources')
    )

def get_book_data(book):
    has_faculty_resources = hasattr(book, 'prefetched_faculty_resources') and bool(book.prefetched_faculty_resources)
    has_student_resources = hasattr(book, 'prefetched_student_resources') and bool(book.prefetched_student_resources)
    try:
        return {
            'id': book.id,
            'slug': f'books/{book.slug}',
            'book_state': book.book_state,
            'title': book.title,
            'subjects': book.subjects(),
            'subject_categories': book.subject_categories,
            'k12subject': book.k12subjects(),
            'is_ap': book.is_ap,
            'is_hs': 'High School' in book.subjects(),
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
            'has_student_resources': has_student_resources,
            'assignable_book': book.assignable_book,
            'promote_snippet': book.promote_snippet.stream_block.get_api_representation(book.promote_snippet),
            'promote_tags': [snippet.value.name for snippet in book.promote_snippet],
        }
    except Exception as e:
        capture_exception(e)
        return None


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
        FieldPanel('link_document'),
        FieldPanel('link_text'),
        FieldPanel('video_reference_number'),
        FieldPanel('updated'),
        FieldPanel('featured'),
    ]


class FacultyResources(models.Model):
    resource = models.ForeignKey(
        snippets.FacultyResource,
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

    def get_resource_icon(self):
        return self.resource.resource_icon

    resource_icon = property(get_resource_icon)

    def get_resource_creator_fest_resource(self):
        return self.resource.creator_fest_resource

    creator_fest_resource = property(get_resource_creator_fest_resource)

    link_external = models.URLField("External link", default='', blank=True,
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

    link_text = models.CharField(max_length=255, null=True, blank=True, help_text="Call to Action Text")
    coming_soon_text = models.CharField(max_length=255, null=True, blank=True,
                                        help_text="If there is text in this field a coming soon banner will be added with this description.")
    video_reference_number = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date resource was updated')
    featured = models.BooleanField(default=False, help_text="Add to featured bar on resource page")
    k12 = models.BooleanField(default=False, help_text="Add K12 banner to resource")
    display_on_k12 = models.BooleanField(default=False, help_text="Display resource on K12 subject pages")
    print_link = models.URLField(blank=True, null=True, help_text="Link for Buy Print link on resource")

    def get_resource_category(self):
        return self.resource.resource_category

    resource_category = property(get_resource_category)

    api_fields = [
        APIField('resource_heading'),
        APIField('resource_description'),
        APIField('resource_unlocked'),
        APIField('resource_icon'),
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
        APIField('display_on_k12'),
        APIField('print_link'),
        APIField('resource_category')
    ]

    panels = [
        FieldPanel('resource'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        FieldPanel('link_document'),
        FieldPanel('link_text'),
        FieldPanel('coming_soon_text'),
        FieldPanel('video_reference_number'),
        FieldPanel('updated'),
        FieldPanel('featured'),
        FieldPanel('k12'),
        FieldPanel('display_on_k12'),
        FieldPanel('print_link')
    ]


class StudentResources(models.Model):
    resource = models.ForeignKey(
        snippets.StudentResource,
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

    def get_resource_icon(self):
        return self.resource.resource_icon

    resource_icon = property(get_resource_icon)

    link_external = models.URLField("External link", default='', blank=True,
                                    help_text="Provide an external URL starting with http:// (or fill out either one of the following two).")
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

    link_text = models.CharField(max_length=255, null=True, blank=True, help_text="Call to Action Text")
    coming_soon_text = models.CharField(max_length=255, null=True, blank=True,
                                        help_text="If there is text in this field a coming soon banner will be added with this description.")
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date resource was updated')
    print_link = models.URLField(blank=True, null=True, help_text="Link for Buy Print link on resource")
    display_on_k12 = models.BooleanField(default=False, help_text="Display resource on K12 subject pages")

    def get_resource_category(self):
        return self.resource.resource_category

    resource_category = property(get_resource_category)

    api_fields = [
        APIField('resource_heading'),
        APIField('resource_description'),
        APIField('resource_unlocked'),
        APIField('resource_icon'),
        APIField('link_external'),
        APIField('link_page'),
        APIField('link_document_url'),
        APIField('link_document_title'),
        APIField('link_text'),
        APIField('coming_soon_text'),
        APIField('updated'),
        APIField('print_link'),
        APIField('display_on_k12'),
        APIField('resource_category')
    ]

    panels = [
        FieldPanel('resource'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        FieldPanel('link_document'),
        FieldPanel('link_text'),
        FieldPanel('coming_soon_text'),
        FieldPanel('updated'),
        FieldPanel('print_link'),
        FieldPanel('display_on_k12')
    ]


class Authors(models.Model):
    name = models.CharField(max_length=255, help_text="Full name of the author.")
    university = models.CharField(max_length=255, null=True, blank=True,
                                  help_text="Name of the university/institution the author is associated with.")
    country = models.CharField(max_length=255, null=True, blank=True,
                               help_text="Country of the university/institution.")
    senior_author = models.BooleanField(default=False,
                                        help_text="Whether the author is a senior author. (Senior authors are shown before non-senior authors.)")
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
    university = blocks.CharBlock(required=False,
                                  help_text="Name of the university/institution the author is associated with.")
    country = blocks.CharBlock(required=False, help_text="Country of the university/institution.")
    senior_author = blocks.BooleanBlock(required=False,
                                        help_text="Whether the author is a senior author. (Senior authors are shown before non-senior authors.)")
    display_at_top = blocks.BooleanBlock(required=False, help_text="Whether display the author on top.")

    class Meta:
        icon = 'user'


class SubjectBooks(models.Model):
    subject = models.ForeignKey(snippets.Subject, on_delete=models.SET_NULL, null=True, related_name='subjects_subject')

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


class K12SubjectBooks(models.Model):
    subject = models.ForeignKey(snippets.K12Subject, on_delete=models.SET_NULL, null=True,
                                related_name='k12subjects_subject')

    def get_subject_name(self):
        return self.subject.name

    subject_name = property(get_subject_name)

    def get_subject_category(self):
        return self.subject.subject_category

    subject_category = property(get_subject_category)

    api_fields = [
        APIField('subject_name'),
        APIField('subject_category'),
    ]


class BookCategory(models.Model):
    category = models.ForeignKey(snippets.SubjectCategory, on_delete=models.SET_NULL, null=True,
                                 related_name='subjects_subjectcategory')

    def get_subject_name(self):
        return self.category.subject_name

    subject_name = property(get_subject_name)

    def get_subject_category(self):
        return self.category.subject_category if self.category is not None else ''

    subject_category = property(get_subject_category)

    api_fields = [
        APIField('subject_name'),
        APIField('subject_category')
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
    content = SharedContentChooserBlock(snippets.SharedContent)
    link = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=False)

    class Meta:
        icon = 'document'
        required = False


class PromoteSnippetContentChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'name': value.name,
                'description': value.description,
                'image': value.promote_image
            }


class PromoteSnippetBlock(blocks.StreamBlock):
    content = PromoteSnippetContentChooserBlock(snippets.PromoteSnippet)

    class Meta:
        icon = 'snippet'
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


class K12BookSubjects(Orderable, K12SubjectBooks):
    k12book_subject = ParentalKey('books.Book', related_name='k12book_subjects')


class BookCategories(Orderable, BookCategory):
    book_category = ParentalKey('books.Book', related_name='book_categories')


class Book(Page):
    licenses = (
        (CC_BY_LICENSE_NAME, CC_BY_LICENSE_NAME),
        (CC_NC_SA_LICENSE_NAME, CC_NC_SA_LICENSE_NAME)
    )

    created = models.DateTimeField(auto_now_add=True)
    book_state = models.CharField(max_length=255, choices=BOOK_STATES, default='live',
                                  help_text='The state of the book.')
    cnx_id = models.CharField(
        max_length=255, help_text="collection.xml UUID. Should be same as book UUID",
        blank=True, null=True)
    book_uuid = models.CharField(
        max_length=255, help_text="collection.xml UUID. Should be same as cnx id.",
        blank=True, null=True)

    polish_site_link = models.URLField(blank=True, null=True,
                                       help_text="Stores target URL to the Polish site so that REX Polish page headers lead back to each individual book on the Polish site")
    salesforce_abbreviation = models.CharField(max_length=255, blank=True, null=True, verbose_name='Subject Book Name',
                                               help_text='This should match the Books Name from Salesforce.')
    salesforce_name = models.CharField(max_length=255, blank=True, null=True,
                                       verbose_name='Name displayed on website forms',
                                       help_text='This is the name shown on interest/adoption forms and used in Partner filtering. The website only shows unique values from here, so it is possible to combine books for forms')
    salesforce_book_id = models.CharField(max_length=255, blank=True, null=True,
                                          help_text='No tracking and not included on adoption and interest forms if left blank)')
    updated = models.DateTimeField(blank=True, null=True, help_text='Late date web content was updated')
    is_ap = models.BooleanField(default=False, help_text='Whether this book is an AP (Advanced Placement) book.')
    description = RichTextField(
        blank=True, help_text="Description shown on Book Detail page.")

    content_warning = models.ForeignKey(
        snippets.ContentWarning,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='content_warnings_content_warning',
        help_text="Message shown in the content warning modal.")

    cover = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The book cover to be shown on the website.'
    )

    def get_cover_url(self):
        if self.cover:
            return build_document_url(self.cover.url)
        else:
            return ''

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

    cover_color = models.CharField(max_length=255, choices=COVER_COLORS, default='blue',
                                   help_text='The color of the cover.')
    book_cover_text_color = models.CharField(max_length=255, choices=BOOK_COVER_TEXT_COLOR, default='yellow',
                                             help_text="Use by the Unified team - this will not change the text color on the book cover.")
    reverse_gradient = models.BooleanField(default=False)
    publish_date = models.DateField(null=True, help_text='Date the book is published on.')
    authors = StreamField([
        ('author', AuthorBlock()),
    ], null=True, use_json_field=True)

    print_isbn_13 = models.CharField(max_length=255, blank=True, null=True,
                                     help_text='ISBN 13 for print version (color).')
    print_softcover_isbn_13 = models.CharField(max_length=255, blank=True, null=True,
                                               help_text='ISBN 13 for print version (black and white).')
    digital_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for digital version.')
    assignable_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for assignable version.')
    ibook_isbn_13 = models.CharField(max_length=255, blank=True, null=True, help_text='ISBN 13 for iBook version.')
    ibook_volume_2_isbn_13 = models.CharField(max_length=255, blank=True, null=True,
                                              help_text='ISBN 13 for iBook v2 version.')
    license_text = models.TextField(
        blank=True, null=True, help_text="Overrides default license text.")
    license_name = models.CharField(
        max_length=255, blank=True, null=True, choices=licenses, default=CC_BY_LICENSE_NAME,
        help_text="Name of the license.")
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

    free_stuff_instructor = StreamField(SharedContentBlock(), null=True, blank=True,
                                        help_text="Snippet to show texts for free instructor resources.",
                                        use_json_field=True)
    free_stuff_student = StreamField(SharedContentBlock(), null=True, blank=True,
                                     help_text="Snipped to show texts for free student resources.", use_json_field=True)
    community_resource_heading = models.CharField(max_length=255, blank=True, null=True,
                                                  help_text="Snipped to show texts for community resources.")
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

    webinar_content = StreamField(SharedContentBlock(), null=True, blank=True, use_json_field=True)
    ibook_link = models.URLField(blank=True, help_text="Link to iBook")
    ibook_link_volume_2 = models.URLField(blank=True, help_text="Link to secondary iBook")
    webview_link = models.URLField(blank=True, help_text="Link to CNX Webview book")
    webview_rex_link = models.URLField(blank=True, help_text="Link to REX Webview book")
    rex_callout_title = models.CharField(max_length=255, blank=True, null=True, help_text='Title of the REX callout',
                                         default="Recommended")
    rex_callout_blurb = models.CharField(max_length=255, blank=True, null=True,
                                         help_text='Additional text for the REX callout.')
    enable_study_edge = models.BooleanField(default=False,
                                            help_text="This will cause the link to the Study Edge app appear on the book details page.")
    bookshare_link = models.URLField(blank=True, help_text="Link to Bookshare resources")
    amazon_coming_soon = models.BooleanField(default=False, verbose_name="Individual Print Coming Soon")
    amazon_link = models.URLField(blank=True, verbose_name="Individual Print Link")
    amazon_iframe = models.TextField(blank=True, null=True, help_text='Amazon iframe code block')
    kindle_link = models.URLField(blank=True, help_text="Link to Kindle version")
    chegg_link = models.URLField(blank=True, null=True, help_text="Link to Chegg e-reader")
    chegg_link_text = models.CharField(max_length=255, blank=True, null=True, help_text='Text for Chegg link.')
    bookstore_coming_soon = models.BooleanField(default=False,
                                                help_text='Whether this book is coming to bookstore soon.')
    bookstore_content = StreamField(SharedContentBlock(), null=True, blank=True, help_text='Bookstore content.',
                                    use_json_field=True)
    comp_copy_available = models.BooleanField(default=True, help_text='Whether free compy available for teachers.')
    comp_copy_content = StreamField(SharedContentBlock(), null=True, blank=True, help_text='Content of the free copy.',
                                    use_json_field=True)
    tutor_marketing_book = models.BooleanField(default=False, help_text='Whether this is a Tutor marketing book.')
    assignable_book = models.BooleanField(default=False, help_text='Whether this is an Assignable book.')
    partner_list_label = models.CharField(max_length=255, null=True, blank=True,
                                          help_text="Controls the heading text on the book detail page for partners. This will update ALL books to use this value!")
    partner_page_link_text = models.CharField(max_length=255, null=True, blank=True,
                                              help_text="Link to partners page on top right of list.")
    featured_resources_header = models.CharField(max_length=255, null=True, blank=True,
                                                 help_text="Featured resource header on instructor resources tab.")
    customization_form_heading = models.CharField(max_length=255, null=True, blank=True,
                                                  help_text="Heading for the CE customization form. This will update ALL books to use this value!",
                                                  default="Customization Form")
    customization_form_subheading = models.CharField(max_length=255, null=True, blank=True,
                                                     help_text="Subheading for the CE customization form. This will update ALL books to use this value!",
                                                     default="Please select the modules (up to 10), that you want to customize with Google Docs.")
    customization_form_disclaimer = RichTextField(blank=True, help_text="This will update ALL books to use this value!",
                                                  default="<p><b>Disclaimer</b></p><p>The following features and functionality are not available to teachers and students using Google Docs customized content:</p><ul><li><b>Errata updates</b>. OpenStax webview is updated at least twice yearly. Customized Google Docs will not receive these content updates.</li><li><b>Access to study tools</b>. OpenStax webview has in-book search, highlighting, study guides, and more available for free. This functionality will not be available in Google Docs versions.</li><li><b>Formatting. </b>Print books and webview have a specific design and structure format developed for those platforms. These functionalities are not available in the Google Docs versions.</li></ul>")
    customization_form_next_steps = RichTextField(blank=True, help_text="This will update ALL books to use this value!",
                                                  default="<p><b>Next Steps</b></p><ol><li>Within two business days, you will receive an email for each module that you have requested access to customize.</li><li>The link provided in the email will be your own copy of the Google Doc that OpenStax generated for you.</li><li>Once you have accessessed the document you can make the changes you desire and share with your students. We recommend using the &quot;Publish to the Web&quot; functionality under the file menu for sharing with students.</li></ol>")
    adoptions = models.IntegerField(blank=True, null=True)
    savings = models.IntegerField(blank=True, null=True)
    support_statement = models.TextField(blank=True, null=True,
                                         default="With philanthropic support, this book is used in <span id='adoption_number'></span> classrooms, saving students <span id='savings'></span> dollars this school year. <a href='/impact'>Learn more about our impact</a> and how you can help.",
                                         help_text="Updating this statement updates it for all book pages.")

    promote_snippet = StreamField(PromoteSnippetBlock(), null=True, blank=True, use_json_field=True)

    videos = StreamField([
        ('video', blocks.ListBlock(blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('description', blocks.RichTextBlock()),
            ('embed', blocks.RawHTMLBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Promote image.'
    )
    translations = StreamField([
        ('translation', blocks.ListBlock(blocks.StructBlock([
            ('locale', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    last_updated_pdf = models.DateTimeField(blank=True, null=True, help_text="Last time PDF was revised.",
                                            verbose_name='PDF Content Revision Date')

    book_detail_panel = Page.content_panels + [
        FieldPanel('book_state'),
        FieldPanel('cnx_id'),
        FieldPanel('book_uuid'),
        FieldPanel('polish_site_link'),
        FieldPanel('salesforce_abbreviation'),
        FieldPanel('salesforce_name'),
        FieldPanel('updated'),
        FieldPanel('publish_date'),
        InlinePanel('book_subjects', label='Subjects'),
        InlinePanel('book_categories', label='Subject Categories'),
        InlinePanel('k12book_subjects', label='K12 Subjects'),
        FieldPanel('is_ap'),
        FieldPanel('description', classname="full"),
        FieldPanel('content_warning'),
        FieldPanel('cover'),
        FieldPanel('title_image'),
        FieldPanel('cover_color'),
        FieldPanel('book_cover_text_color'),
        FieldPanel('reverse_gradient'),
        FieldPanel('print_isbn_13'),
        FieldPanel('print_softcover_isbn_13'),
        FieldPanel('digital_isbn_13'),
        FieldPanel('ibook_isbn_13'),
        FieldPanel('ibook_volume_2_isbn_13'),
        FieldPanel('license_text'),
        FieldPanel('license_name'),
        FieldPanel('webview_rex_link'),
        FieldPanel('rex_callout_title'),
        FieldPanel('rex_callout_blurb'),
        FieldPanel('enable_study_edge'),
        FieldPanel('high_resolution_pdf'),
        FieldPanel('last_updated_pdf'),
        FieldPanel('low_resolution_pdf'),
        FieldPanel('free_stuff_instructor'),
        FieldPanel('free_stuff_student'),
        FieldPanel('community_resource_heading'),
        FieldPanel('community_resource_logo'),
        FieldPanel('community_resource_url'),
        FieldPanel('community_resource_cta'),
        FieldPanel('community_resource_blurb'),
        FieldPanel('community_resource_feature_link'),
        FieldPanel('community_resource_feature_text'),
        FieldPanel('webinar_content'),
        FieldPanel('ibook_link'),
        FieldPanel('ibook_link_volume_2'),
        FieldPanel('bookshare_link'),
        FieldPanel('amazon_coming_soon'),
        FieldPanel('amazon_link'),
        FieldPanel('amazon_iframe'),
        FieldPanel('kindle_link'),
        FieldPanel('chegg_link'),
        FieldPanel('chegg_link_text'),
        FieldPanel('bookstore_coming_soon'),
        FieldPanel('bookstore_content'),
        FieldPanel('comp_copy_available'),
        FieldPanel('comp_copy_content'),
        FieldPanel('tutor_marketing_book'),
        FieldPanel('assignable_book'),
        FieldPanel('promote_snippet'),
        FieldPanel('partner_list_label'),
        FieldPanel('partner_page_link_text'),
        FieldPanel('customization_form_heading'),
        FieldPanel('customization_form_subheading'),
        FieldPanel('customization_form_disclaimer'),
        FieldPanel('customization_form_next_steps'),
        FieldPanel('support_statement'),
        FieldPanel('videos'),
        FieldPanel('translations'),
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
        FieldPanel('authors')
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel('promote_image'),
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
        APIField('book_uuid'),
        APIField('polish_site_link'),
        APIField('salesforce_abbreviation'),
        APIField('salesforce_name'),
        APIField('salesforce_book_id'),
        APIField('book_subjects'),
        APIField('book_categories'),
        APIField('k12book_subjects'),
        APIField('is_ap'),
        APIField('description'),
        APIField('content_warning_text'),
        APIField('cover_url'),
        APIField('title_image_url'),
        APIField('cover_color'),
        APIField('book_cover_text_color'),
        APIField('reverse_gradient'),
        APIField('book_student_resources'),
        APIField('book_faculty_resources'),
        APIField('publish_date'),
        APIField('authors'),
        APIField('print_isbn_13'),
        APIField('print_softcover_isbn_13'),
        APIField('digital_isbn_13'),
        APIField('ibook_isbn_13'),
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
        APIField('promote_snippet'),
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
        APIField('amazon_iframe'),
        APIField('kindle_link'),
        APIField('chegg_link'),
        APIField('chegg_link_text'),
        APIField('bookstore_coming_soon'),
        APIField('bookstore_content'),
        APIField('comp_copy_available'),
        APIField('comp_copy_content'),
        APIField('errata_content'),
        APIField('tutor_marketing_book'),
        APIField('assignable_book'),
        APIField('partner_list_label'),
        APIField('partner_page_link_text'),
        APIField('customization_form_heading'),
        APIField('customization_form_subheading'),
        APIField('customization_form_disclaimer'),
        APIField('customization_form_next_steps'),
        APIField('videos'),
        APIField('translations'),
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

    def k12subjects(self):
        k12subject_list = []
        for k12subject in self.k12book_subjects.all():
            k12subject_list.append(k12subject.subject_name)
        return k12subject_list

    @property
    def subject_categories(self):
        category_list = []
        if self.book_categories is not None:
            for category in self.book_categories.all():
                if category is not None:
                    category_list.append(category.subject_category)
        return category_list

    @property
    def errata_content(self):
        if self.locale == 'es':
            return snippets.ErrataContent.objects.filter(locale=self.locale).first().content
        return snippets.ErrataContent.objects.filter(book_state=self.book_state, locale=self.locale).first().content

    @property
    def content_warning_text(self):
        return self.content_warning.content_warning if self.content_warning else None

    def get_slug(self):
        return 'books/{}'.format(self.slug)

    def book_urls(self):
        book_urls = []
        for field in self.api_fields:
            try:
                url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                 getattr(self, field))
                if url:
                    book_urls.append(url)
            except(TypeError, AttributeError):
                pass
        return book_urls

    def save(self, *args, **kwargs):
        if self.partner_list_label:
            Book.objects.filter(locale=self.locale).update(partner_list_label=self.partner_list_label)

        if self.partner_page_link_text:
            Book.objects.filter(locale=self.locale).update(partner_page_link_text=self.partner_page_link_text)

        # sync customization form changes on all books
        if self.customization_form_heading:
            Book.objects.filter(locale=self.locale).update(customization_form_heading=self.customization_form_heading)
        if self.customization_form_subheading:
            Book.objects.filter(locale=self.locale).update(
                customization_form_subheading=self.customization_form_subheading)
        if self.customization_form_disclaimer:
            Book.objects.filter(locale=self.locale).update(
                customization_form_disclaimer=self.customization_form_disclaimer)
        if self.customization_form_next_steps:
            Book.objects.filter(locale=self.locale).update(
                customization_form_next_steps=self.customization_form_next_steps)
        if self.support_statement:
            Book.objects.filter(locale=self.locale).update(support_statement=self.support_statement)

        # populate license
        if self.license_name:
            if self.license_name == CC_BY_LICENSE_NAME:
                self.license_url = CC_BY_LICENSE_URL
                self.license_version = CC_BY_LICENSE_VERSION
            else:
                self.license_url = CC_NC_SA_LICENSE_URL
                self.license_version = CC_NC_SA_LICENSE_VERSION

        from salesforce.functions import retrieve_salesforce_names
        if self.salesforce_book_id:
            salesforce_names = retrieve_salesforce_names(self.salesforce_book_id)
            if len(salesforce_names) > 0:
                self.salesforce_abbreviation = salesforce_names['Name']
                self.salesforce_name = salesforce_names['Official_Name']

        return super(Book, self).save(*args, **kwargs)

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/details/books/{}'.format(self.slug)

    def __str__(self):
        return self.book_title


# old subjects interface, deprecated
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
    dev_standard_4_description = models.TextField(
        help_text="Keep <span> in place to populate with Salesforce data. id=adoption_number for classrooms and id=savings for savings number.")
    subject_list_heading = models.CharField(
        max_length=255, blank=True, null=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    translations = StreamField([
        ('translation', blocks.ListBlock(blocks.StructBlock([
            ('locale', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    @property
    def books(self):
        books = Book.objects.live().filter(locale=self.locale).exclude(book_state='unlisted').order_by('title')
        book_data = []
        for book in books:
            data = get_book_data(book)
            if data:
                book_data.append(data)
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
        FieldPanel('translations'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
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
        APIField('translations'),
        APIField('books'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
    ]

    template = 'page.html'

    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    subpage_types = ['books.Book']
    max_count = 1

    # BookIndex model is old subjects interface and is deprecated
    def get_url_parts(self, *args, **kwargs):
        return None

    def get_sitemap_urls(self, request=None):
        return []
