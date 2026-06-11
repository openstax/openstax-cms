from django.db import models
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.api import APIField

from openstax.api_fields import ExpandedRichTextField
from openstax.preview import FrontendPreviewMixin
from books.models import Book, BookFacultyResources, BookStudentResources


from pages.custom_blocks import FAQBlock, \
    CardImageBlock, \
    TestimonialBlock

import snippets.models as snippets



class K12MainPage(FrontendPreviewMixin, Page):
    banner_headline = models.CharField(default='', blank=True, max_length=255)
    banner_description = models.TextField(default='', blank=True)
    banner_right_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subject_list_default = models.CharField(default='Find Your Subject', blank=True, max_length=255)
    features_cards = StreamField([
        ('features_cards', CardImageBlock()),
    ], use_json_field=True)
    highlights_header = RichTextField(default='', blank=True)
    highlights = StreamField(
        blocks.StreamBlock([
            ('highlight', blocks.ListBlock(blocks.StructBlock([
                ('highlight_subheader', blocks.TextBlock(required=False)),
                ('highlight_text', blocks.CharBlock(Required=False)),
            ])))], max_num=3), use_json_field=True)
    highlights_icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    stats_grid = StreamField(
        blocks.StreamBlock([
            ('stat', blocks.ListBlock(blocks.StructBlock([
                ('bold_stat_text', blocks.TextBlock(required=False)),
                ('normal_stat_text', blocks.CharBlock(required=False)),
            ])))], max_num=3), use_json_field=True)
    stats_image1 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    stats_image2 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    stats_image3 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subject_library_header = models.CharField(default='', blank=True, max_length=255)
    subject_library_description = models.TextField(default='', blank=True)
    testimonials_header = models.CharField(default='', blank=True, max_length=255)
    testimonials_description = models.TextField(default='', blank=True)
    testimonials = StreamField([
        ('testimonials', TestimonialBlock()),
    ], use_json_field=True)
    faq_header = models.CharField(default='', blank=True, max_length=255)
    faqs = StreamField([
        ('faq', FAQBlock()),
    ], use_json_field=True)
    rfi_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    rfi_header = models.CharField(default='', blank=True, max_length=255)
    rfi_description = models.TextField(default='', blank=True)
    sticky_header = models.CharField(default='', blank=True, max_length=255)
    sticky_description = models.TextField(default='', blank=True)

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /k12
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return (site_id, site_root_url, '/k12')

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def k12library(self):
        subject_list = {}
        for subject in snippets.K12Subject.objects.filter(locale=self.locale).order_by('name'):
            subject_categories = {}
            subject_categories['color'] = subject.subject_color
            subject_categories['image'] = subject.subject_image
            subject_categories['link'] = subject.subject_link
            subject_categories['subject_category'] = subject.subject_category
            subject_list[subject.name] = subject_categories
        return subject_list

    api_fields = [
        APIField('title'),
        APIField('banner_headline'),
        APIField('banner_description'),
        APIField('banner_right_image'),
        APIField('subject_list_default'),
        APIField('features_cards'),
        APIField('highlights_header', serializer=ExpandedRichTextField()),
        APIField('highlights'),
        APIField('highlights_icon'),
        APIField('stats_grid'),
        APIField('stats_image1'),
        APIField('stats_image2'),
        APIField('stats_image3'),
        APIField('subject_library_header'),
        APIField('subject_library_description'),
        APIField('k12library'),
        APIField('testimonials_header'),
        APIField('testimonials_description'),
        APIField('testimonials'),
        APIField('faq_header'),
        APIField('faqs'),
        APIField('rfi_image'),
        APIField('rfi_header'),
        APIField('rfi_description'),
        APIField('sticky_header'),
        APIField('sticky_description'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    class Meta:
        verbose_name = "K12 Main Page"

    content_panels = [
        TitleFieldPanel('title', classname="full title"),
        FieldPanel('banner_headline'),
        FieldPanel('banner_description'),
        FieldPanel('banner_right_image'),
        FieldPanel('features_cards'),
        FieldPanel('highlights_header'),
        FieldPanel('highlights'),
        FieldPanel('highlights_icon'),
        FieldPanel('stats_grid'),
        FieldPanel('stats_image1'),
        FieldPanel('stats_image2'),
        FieldPanel('stats_image3'),
        FieldPanel('subject_library_header'),
        FieldPanel('subject_library_description'),
        FieldPanel('testimonials_header'),
        FieldPanel('testimonials_description'),
        FieldPanel('testimonials'),
        FieldPanel('faq_header'),
        FieldPanel('faqs'),
        FieldPanel('rfi_image'),
        FieldPanel('rfi_header'),
        FieldPanel('rfi_description'),
        FieldPanel('sticky_header'),
        FieldPanel('sticky_description')
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    max_count = 1
    template = 'page.html'
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    subpage_types = ['pages.K12Subject']


class K12Subject(FrontendPreviewMixin, Page):
    subheader = models.TextField(default='HIGH SCHOOL')
    books_heading = models.TextField(default='')
    books_short_desc = RichTextField(default='')
    about_books_heading = models.TextField(default='About the Books')
    about_books_text = models.CharField(default='FIND SUPPLEMENTAL RESOURCES', blank=True, max_length=255)
    adoption_heading = models.TextField(default='Using an OpenStax resource in your classroom? Let us know!')
    adoption_text = RichTextField(
        default="<p>Help us continue to make high-quality educational materials accessible by letting us know you've adopted! Our future grant funding is based on educator adoptions and the number of students we impact.</p>")
    adoption_link_text = models.CharField(default='Report Your Adoption', max_length=255)
    adoption_link = models.URLField(blank=True, default='/adoption')
    quote_heading = models.TextField(default='What Our Teachers Say', blank=True, )
    quote_text = models.CharField(default='', blank=True, max_length=255)
    resources_heading = models.TextField(default='Supplemental Resources')
    blogs_heading = models.TextField(default='Blogs for High School Teachers', blank=True, )
    rfi_heading = models.TextField(default="Don't see what you're looking for?")
    rfi_text = models.CharField(
        default="We're here to answer any questions you may have. Complete the form to get in contact with a member of our team.",
        max_length=255)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def subject_intro(self):
        for subject in snippets.K12Subject.objects.filter(locale=self.locale, name=self.title).order_by('name'):
            subject_intro = subject.intro_text
        return subject_intro

    @property
    def subject_image(self):
        for subject in snippets.K12Subject.objects.filter(locale=self.locale, name=self.title).order_by('name'):
            subject_image = subject.subject_image
        return subject_image

    @property
    def subject_category(self):
        for subject in snippets.K12Subject.objects.filter(locale=self.locale, name=self.title).order_by('name'):
            subject_category = subject.subject_category
        return subject_category

    @property
    def books(self):
        books = Book.objects.order_by('path')
        book_data = []
        for book in books:
            k12subjects = []
            for subject in book.k12book_subjects.all():
                k12subjects.append(subject.subject_name)
            subjects = []
            for subject in book.book_subjects.all():
                subjects.append(subject.subject_name)
            if book.k12book_subjects is not None \
                    and self.title in k12subjects \
                    and book.book_state not in ['retired', 'draft']:
                book_data.append({
                    'id': book.id,
                    'slug': 'books/{}'.format(book.slug),
                    'title': book.title,
                    'description': book.description,
                    'cover_url': book.cover_url,
                    'is_ap': book.is_ap,
                    'is_hs': 'High School' in subjects,
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
                    'updated': book.updated,
                    'created': book.created,
                    'publish_date': book.publish_date,
                    'last_updated_pdf': book.last_updated_pdf
                })
        return book_data

    def student_resource_headers(self):
        student_resource_data = []
        book_ids = {}
        for book in self.books:
            book_id = book.get('id')
            book_title = book.get('title')
            book_ids[book_id] = book_title
        for resource in BookStudentResources.objects.filter(display_on_k12=True,
                                                            book_student_resource_id__in=book_ids).all():
            link_document_url = None
            if resource.link_document_id is not None:
                link_document_url = resource.link_document_url
            student_resource_data.append({
                'id': resource.id,
                'heading': resource.get_resource_heading(),
                'icon': resource.get_resource_icon(),
                'book': book_ids[resource.book_student_resource_id],
                'resource_id': resource.resource_id,
                'resource_unlocked': resource.resource_unlocked,
                'link_external': resource.link_external,
                'link_page': resource.link_page,
                'link_document_url': link_document_url,
                'link_text': resource.link_text,
                'coming_soon_text': resource.coming_soon_text,
                'updated': resource.updated,
                'print_link': resource.print_link,
                'display_on_k12': resource.display_on_k12,
                'resource_category': resource.resource_category,
            })
        return student_resource_data

    def faculty_resource_headers(self):
        faculty_resource_data = []
        book_ids = {}
        for book in self.books:
            book_id = book.get('id')
            book_title = book.get('title')
            book_ids[book_id] = book_title
        for resource in BookFacultyResources.objects.filter(display_on_k12=True,
                                                            book_faculty_resource_id__in=book_ids).all():
            link_document_url = None
            if resource.link_document_id is not None:
                link_document_url = resource.link_document_url
            faculty_resource_data.append({
                'id': resource.id,
                'heading': resource.get_resource_heading(),
                'icon': resource.get_resource_icon(),
                'book': book_ids[resource.book_faculty_resource_id],
                'resource_id': resource.resource_id,
                'resource_unlocked': resource.resource_unlocked,
                'link_external': resource.link_external,
                'link_page_id': resource.link_page_id,
                'link_document_url': link_document_url,
                'link_text': resource.link_text,
                'coming_soon_text': resource.coming_soon_text,
                'updated': resource.updated,
                'print_link': resource.print_link,
                'k12': resource.k12,
                'display_on_k12': resource.display_on_k12,
                'resource_category': resource.resource_category,
            })
        return faculty_resource_data

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/k12/{}'.format(self.slug[4:])

    api_fields = [
        APIField('subheader'),
        APIField('subject_intro'),
        APIField('subject_image'),
        APIField('subject_category'),
        APIField('books_heading'),
        APIField('books_short_desc', serializer=ExpandedRichTextField()),
        APIField('about_books_heading'),
        APIField('about_books_text'),
        APIField('books'),
        APIField('student_resource_headers'),
        APIField('faculty_resource_headers'),
        APIField('adoption_heading'),
        APIField('adoption_text', serializer=ExpandedRichTextField()),
        APIField('adoption_link_text'),
        APIField('adoption_link'),
        APIField('quote_heading'),
        APIField('quote_text'),
        APIField('resources_heading'),
        APIField('blogs_heading'),
        APIField('rfi_heading'),
        APIField('rfi_text'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('subheader'),
        FieldPanel('books_heading'),
        FieldPanel('books_short_desc'),
        FieldPanel('about_books_heading'),
        FieldPanel('about_books_text'),
        FieldPanel('adoption_heading'),
        FieldPanel('adoption_text'),
        FieldPanel('adoption_link_text'),
        FieldPanel('adoption_link'),
        FieldPanel('quote_heading'),
        FieldPanel('quote_text'),
        FieldPanel('resources_heading'),
        FieldPanel('blogs_heading'),
        FieldPanel('rfi_heading'),
        FieldPanel('rfi_text'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.K12MainPage']

    class Meta:
        verbose_name = "K12 Subject"


