from collections import defaultdict

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.api import APIField

from openstax.preview import FrontendPreviewMixin
from books.models import Book, SubjectBooks


from pages.custom_blocks import TutorAdBlock, \
    AboutOpenStaxBlock, \
    InfoBoxBlock

import snippets.models as snippets



class Subjects(FrontendPreviewMixin, Page):
    heading = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    heading_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tutor_ad = StreamField([
        ('content', TutorAdBlock()),
    ], use_json_field=True)

    about_os = StreamField([
        ('content', AboutOpenStaxBlock()),
    ], use_json_field=True)

    info_boxes = StreamField([
        ('info_box', blocks.ListBlock(InfoBoxBlock())),
    ], use_json_field=True)

    philanthropic_support = models.TextField(blank=True, null=True)
    translations = StreamField([
        ('translation', blocks.ListBlock(blocks.StructBlock([
            ('locale', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def subjects(self):
        subject_list = {}
        subjects = list(snippets.Subject.objects.filter(locale=self.locale).order_by('name'))
        if not subjects:
            return subject_list
        subject_ids = [subject.id for subject in subjects]
        categories_by_subject_id = defaultdict(list)
        for category in snippets.SubjectCategory.objects.filter(subject_id__in=subject_ids).order_by('subject_category'):
            categories_by_subject_id[category.subject_id].append(category.subject_category)

        for subject in subjects:
            subject_categories = {}
            subject_categories['icon'] = subject.subject_icon
            subject_categories['categories'] = categories_by_subject_id.get(subject.id, [])
            subject_list[subject.name] = subject_categories

        return subject_list

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /subjects
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/subjects'

    api_fields = [
        APIField('heading'),
        APIField('description'),
        APIField('heading_image'),
        APIField('tutor_ad'),
        APIField('about_os'),
        APIField('info_boxes'),
        APIField('philanthropic_support'),
        APIField('subjects'),
        APIField('translations'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('heading_image'),
        FieldPanel('tutor_ad'),
        FieldPanel('about_os'),
        FieldPanel('info_boxes'),
        FieldPanel('philanthropic_support'),
        FieldPanel('translations'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.RootPage']
    subpage_types = ['pages.Subject']
    max_count = 1

    class Meta:
        verbose_name = "New Subjects Page"


class SubjectOrderable(Orderable, SubjectBooks):
    page = ParentalKey("pages.Subject", related_name="subject")

    panels = [
        FieldPanel("subject"),
    ]


class Subject(FrontendPreviewMixin, Page):
    page_description = models.TextField(default='')
    tutor_ad = StreamField([
        ('content', TutorAdBlock()),
    ], null=True, blank=True, use_json_field=True)

    blog_header = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('blog_description', blocks.TextBlock()),
                ('link_text', blocks.CharBlock()),
                ('link_href', blocks.URLBlock())
            ]))], max_num=1), use_json_field=True)

    webinar_header = StreamField(
        blocks.StreamBlock([
            ('content', blocks.StructBlock([
                ('heading', blocks.CharBlock()),
                ('webinar_description', blocks.TextBlock()),
                ('link_text', blocks.CharBlock()),
                ('link_href', blocks.URLBlock())
            ]))], max_num=1), use_json_field=True)

    os_textbook_heading = models.TextField(blank=True, null=True)
    os_textbook_categories = StreamField([
        ('category', blocks.ListBlock(blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('text', blocks.TextBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    about_os = StreamField([
        ('content', AboutOpenStaxBlock()),
    ], use_json_field=True)

    info_boxes = StreamField([
        ('info_box', blocks.ListBlock(InfoBoxBlock())),
    ], use_json_field=True)
    book_categories_heading = models.TextField(default='')
    learn_more_heading = models.TextField(default='')
    learn_more_blog_posts = models.TextField(default='')
    learn_more_webinars = models.TextField(default='')
    learn_more_about_books = models.TextField(default='')

    philanthropic_support = models.TextField(blank=True, null=True)
    translations = StreamField([
        ('translation', blocks.ListBlock(blocks.StructBlock([
            ('locale', blocks.CharBlock()),
            ('slug', blocks.CharBlock()),
        ])))
    ], null=True, blank=True, use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /subjects
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/subjects/{}'.format(self.slug[0:-6])

    @property
    def selected_subject(self):
        return self.subject.all()

    @property
    def subjects(self):
        subject_list = {}
        first_selected = self.selected_subject.first()
        if first_selected is None:
            return subject_list
        selected_subjects = list(snippets.Subject.objects.filter(name=str(first_selected.subject_name), locale=self.locale))
        subject_ids = [subject.id for subject in selected_subjects]
        categories_by_subject_id = defaultdict(list)
        for category in snippets.SubjectCategory.objects.filter(subject_id__in=subject_ids).order_by('subject_category'):
            categories_by_subject_id[category.subject_id].append(category)

        for subject in selected_subjects:
            subject_categories = {}
            categories = {}

            subject_categories['icon'] = subject.subject_icon
            all_books = Book.objects.filter(book_subjects__subject=subject).exclude(
                book_state__in=['retired', 'unlisted']
            ).prefetch_related('book_subjects__subject', 'book_categories__category').order_by('title').distinct()
            for category in categories_by_subject_id.get(subject.id, []):
                books = {}
                book_list = {}
                for book in all_books:
                    if book.subject_categories is not None \
                            and category.subject_category in book.subject_categories:
                        book_data = []
                        book_data.append({
                            'id': book.id,
                            'slug': 'books/{}'.format(book.slug),
                            'book_state': book.book_state,
                            'title': book.title,
                            'subjects': book.subjects(),
                            'subject_categories': book.subject_categories,
                            'k12subject': book.k12subjects(),
                            'is_ap': book.is_ap,
                            'cover_url': book.cover_url,
                            'cover_color': book.cover_color,
                            'pdf_url': book.pdf_url,
                            'high_resolution_pdf_url': book.pdf_url,  # deprecated alias
                            'webview_link': book.webview_link,
                            'webview_rex_link': book.webview_rex_link,
                            'bookshare_link': book.bookshare_link,
                            'amazon_coming_soon': book.amazon_coming_soon,
                            'amazon_link': book.amazon_link,
                            'bookstore_coming_soon': book.bookstore_coming_soon,
                            'salesforce_abbreviation': book.salesforce_abbreviation,
                            'salesforce_name': book.salesforce_name,
                            'urls': book.book_urls(),
                            'last_updated_pdf': book.last_updated_pdf,
                        })
                        books[book.title] = book_data
                book_list['category_description'] = category.description
                book_list['books'] = books
                categories[category.subject_category] = book_list
            subject_categories['categories'] = categories
            subject_list[subject.name] = subject_categories

        return subject_list

    api_fields = [
        APIField('page_description'),
        APIField('tutor_ad'),
        APIField('blog_header'),
        APIField('webinar_header'),
        APIField('os_textbook_heading'),
        APIField('os_textbook_categories'),
        APIField('about_os'),
        APIField('info_boxes'),
        APIField('book_categories_heading'),
        APIField('learn_more_heading'),
        APIField('learn_more_blog_posts'),
        APIField('learn_more_webinars'),
        APIField('learn_more_about_books'),
        APIField('philanthropic_support'),
        APIField('subjects'),
        APIField('translations'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([InlinePanel("subject", label="Subject", min_num=1, max_num=1)], heading="Subject(s)"),
        FieldPanel('page_description'),
        FieldPanel('tutor_ad'),
        FieldPanel('blog_header'),
        FieldPanel('webinar_header'),
        FieldPanel('os_textbook_heading'),
        FieldPanel('os_textbook_categories'),
        FieldPanel('about_os'),
        FieldPanel('info_boxes'),
        FieldPanel('book_categories_heading'),
        FieldPanel('learn_more_heading'),
        FieldPanel('learn_more_blog_posts'),
        FieldPanel('learn_more_webinars'),
        FieldPanel('learn_more_about_books'),
        FieldPanel('philanthropic_support'),
        FieldPanel('translations'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    template = 'page.html'

    parent_page_types = ['pages.Subjects']

    class Meta:
        verbose_name = "Subject Page"

