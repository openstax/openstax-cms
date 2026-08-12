import datetime
import json
from unittest import mock

import vcr
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.documents.models import Document
from wagtail.models import Page, Site

from pages.table_sources import build_cell, build_table, field_choices


class BuildCellTests(TestCase):
    def test_text_cell_escapes_html(self):
        cell = build_cell('<script>x</script>', 'text')
        self.assertEqual(cell['cta'], [])
        self.assertNotIn('<script>', cell['content'])
        self.assertIn('&lt;script&gt;', cell['content'])

    def test_empty_value_yields_empty_cell(self):
        self.assertEqual(build_cell(None, 'text'), {'content': '', 'cta': []})
        self.assertEqual(build_cell('', 'text'), {'content': '', 'cta': []})

    def test_date_cell_formats_mm_dd_yyyy(self):
        cell = build_cell(datetime.date(2018, 3, 28), 'date')
        self.assertEqual(cell['content'], '03/28/2018')

    def test_number_cell_stringifies(self):
        self.assertEqual(build_cell(42, 'number')['content'], '42')

    def test_link_cell_builds_cta_shape(self):
        cell = build_cell({'text': 'Biology 2e', 'url': '/details/books/biology-2e'}, 'link')
        self.assertEqual(cell['content'], '')
        cta = cell['cta'][0]
        self.assertEqual(cta['text'], 'Biology 2e')
        self.assertEqual(cta['target'], {'value': '/details/books/biology-2e', 'type': 'internal'})
        self.assertEqual(cta['aria_label'], '')
        self.assertEqual(cta['config'], [])

    def test_link_cell_absolute_url_is_external(self):
        cell = build_cell({'text': 'Read', 'url': 'https://example.com/x'}, 'link')
        self.assertEqual(cell['cta'][0]['target']['type'], 'external')

    def test_link_cell_without_url_falls_back_to_text(self):
        cell = build_cell({'text': 'No link', 'url': ''}, 'link')
        self.assertEqual(cell['cta'], [])
        self.assertEqual(cell['content'], 'No link')

    def test_image_cell_renders_img_tag(self):
        cell = build_cell({'url': 'https://assets.openstax.org/x.png', 'alt': 'Cover'}, 'image')
        self.assertIn('<img', cell['content'])
        self.assertIn('src="https://assets.openstax.org/x.png"', cell['content'])
        self.assertIn('alt="Cover"', cell['content'])

    def test_html_cell_passes_through(self):
        cell = build_cell('<p>rich</p>', 'html')
        self.assertEqual(cell['content'], '<p>rich</p>')

    def test_link_cell_mailto_and_protocol_relative_are_external(self):
        for url in ['mailto:info@openstax.org', 'tel:+17133486000', '//cdn.example.com/x']:
            cell = build_cell({'text': 'Contact', 'url': url}, 'link')
            self.assertEqual(cell['cta'][0]['target']['type'], 'external', url)

    def test_link_cell_dangerous_scheme_degrades_to_text(self):
        for url in ['javascript:alert(1)', 'data:text/html,x',
                    'vbscript:msgbox', 'file:///etc/passwd']:
            cell = build_cell({'text': 'Click', 'url': url}, 'link')
            self.assertEqual(cell['cta'], [], url)
            self.assertEqual(cell['content'], 'Click', url)

    def test_link_cell_safe_schemes_and_paths_still_link(self):
        for url in ['https://example.com/x', 'mailto:info@openstax.org',
                    'tel:+17133486000', '//cdn.example.com/x',
                    '/details/books/biology-2e']:
            cell = build_cell({'text': 'Go', 'url': url}, 'link')
            self.assertEqual(cell['cta'][0]['target']['value'], url, url)

    def test_date_cell_non_date_fallback_is_escaped(self):
        cell = build_cell('<b>not a date</b>', 'date')
        self.assertNotIn('<b>', cell['content'])
        self.assertIn('&lt;b&gt;', cell['content'])

    def test_link_cell_scalar_raw_is_treated_as_url(self):
        cell = build_cell('https://example.com/x', 'link')
        self.assertEqual(cell['cta'][0]['target']['value'], 'https://example.com/x')
        self.assertEqual(cell['cta'][0]['target']['type'], 'external')


class BuildTableTests(TestCase):
    REGISTRY = {
        'name': ('Name', lambda item: item['name'], 'text'),
        'when': ('Date', lambda item: item['when'], 'date'),
        'boom': ('Boom', lambda item: 1 / 0, 'text'),
    }

    def test_builds_columns_and_rows_from_registry(self):
        result = build_table(
            [{'field': 'name', 'header': '', 'type': ''},
             {'field': 'when', 'header': 'Published', 'type': ''}],
            self.REGISTRY,
            [{'name': 'Biology 2e', 'when': datetime.date(2018, 3, 28)}],
        )
        self.assertEqual(result['columns'], [
            {'header': 'Name', 'type': 'text'},
            {'header': 'Published', 'type': 'date'},
        ])
        cells = result['rows'][0]['cells']
        self.assertEqual(cells[0]['content'], 'Biology 2e')
        self.assertEqual(cells[1]['content'], '03/28/2018')

    def test_explicit_type_overrides_registry_default(self):
        result = build_table(
            [{'field': 'when', 'header': '', 'type': 'text'}],
            self.REGISTRY,
            [{'when': datetime.date(2018, 3, 28)}],
        )
        self.assertEqual(result['columns'][0]['type'], 'text')

    def test_failing_getter_yields_empty_cell_not_error(self):
        result = build_table(
            [{'field': 'boom', 'header': '', 'type': ''}],
            self.REGISTRY,
            [{'name': 'x'}],
        )
        self.assertEqual(result['rows'][0]['cells'][0], {'content': '', 'cta': []})

    def test_field_choices_from_registry(self):
        self.assertIn(('name', 'Name'), field_choices(self.REGISTRY))

    def test_unknown_field_is_skipped_without_error(self):
        result = build_table(
            [{'field': 'gone', 'header': '', 'type': ''},
             {'field': 'name', 'header': '', 'type': ''}],
            self.REGISTRY,
            [{'name': 'x'}],
        )
        self.assertEqual(len(result['columns']), 1)
        self.assertEqual(len(result['rows'][0]['cells']), 1)
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'x')

    def test_failing_cell_build_degrades_to_empty_cell(self):
        # After the link-branch guard (build_cell), no registry-reachable raw
        # value makes build_cell itself raise anymore, so this documents the
        # build_table containment directly: force build_cell to raise and
        # confirm one bad cell degrades to empty instead of killing the row.
        registry = {'bad': ('Bad', lambda item: object(), 'date')}
        with mock.patch('pages.table_sources.build_cell', side_effect=RuntimeError('boom')):
            result = build_table([{'field': 'bad', 'header': '', 'type': ''}], registry, [{}])
        self.assertEqual(result['rows'][0]['cells'][0], {'content': '', 'cta': []})

    def test_link_column_collapses_to_text_column_type(self):
        registry = {'link': ('Link', lambda item: {'text': 't', 'url': '/x'}, 'link')}
        result = build_table(
            [{'field': 'link', 'header': '', 'type': ''}],
            registry,
            [{}],
        )
        self.assertEqual(result['columns'][0]['type'], 'text')


class BooksSourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from books.models import BookIndex
        from pages.models import RootPage
        root_page = Page.objects.get(title="Root")
        homepage = RootPage(title="Hello World", slug="openstax-homepage")
        root_page.add_child(instance=homepage)
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test")
        homepage.add_child(instance=book_index)
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        with open("pages/static/images/openstax.png", 'rb') as image_file:
            test_image = SimpleUploadedFile(
                name='openstax.png', content=image_file.read())
        cls.test_doc = Document.objects.create(title='Test Doc', file=test_image)
        cls.book_index = book_index

    def _make_book(self, **overrides):
        import datetime
        from books.models import Book
        data = dict(title="University Physics",
                    slug="university-physics",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_book_id='a0ZU0000008pyvQMAQ',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date(2016, 8, 3),
                    locale=self.book_index.locale)
        data.update(overrides)
        book = Book(**data)
        self.book_index.add_child(instance=book)
        return book

    def test_resolve_books_builds_rows(self):
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            self._make_book()
        result = resolve_books({
            'subject': None, 'book_state': 'live', 'order': 'title', 'limit': 10,
            'columns': [
                {'field': 'title', 'header': '', 'type': ''},
                {'field': 'publish_date', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(result['columns'][0], {'header': 'Title', 'type': 'text'})
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'University Physics')
        self.assertEqual(result['rows'][0]['cells'][1]['content'], '08/03/2016')

    def test_resolve_books_title_link_builds_details_cta(self):
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            self._make_book()
        result = resolve_books({
            'subject': None, 'book_state': 'live', 'order': 'title', 'limit': 10,
            'columns': [{'field': 'title_link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['text'], 'University Physics')
        self.assertEqual(cta['target'],
                         {'value': '/details/books/university-physics', 'type': 'internal'})

    def test_resolve_books_filters_by_state(self):
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            self._make_book(book_state='retired')
        result = resolve_books({
            'subject': None, 'book_state': 'live', 'order': 'title', 'limit': 10,
            'columns': [{'field': 'title', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'], [])

    def test_resolve_books_excludes_retired_when_state_filter_empty(self):
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            self._make_book(book_state='retired')
        result = resolve_books({
            'subject': None, 'book_state': '', 'order': 'title', 'limit': 10,
            'columns': [{'field': 'title', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'], [])

    def test_resolve_books_omitting_remediation_matches_pre_change_output(self):
        # Regression: a config dict saved before this feature has no
        # 'remediation' key at all — behavior must be identical to 'All'.
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            self._make_book()
        result = resolve_books({
            'subject': None, 'book_state': 'live', 'order': 'title', 'limit': 10,
            'columns': [{'field': 'title', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'University Physics')

    def test_resolve_books_remediation_clear_requires_tracked_and_no_outstanding(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            clear_book = self._make_book(remediation_status='fixed')
            outstanding_book = self._make_book(title='College Physics', slug='college-physics')
            untracked_book = self._make_book(title='Chemistry', slug='chemistry')
        # clear_book: book status tracked (fixed) and its one resource is fixed too.
        clear_snippet = FacultyResource.objects.create(
            heading='Slides', description='<p>x</p>', unlocked_resource=True,
            locale=clear_book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=clear_book, resource=clear_snippet,
            link_external='https://x.co', remediation_status='fixed')
        # outstanding_book: nothing on the book itself, but a resource is in progress.
        outstanding_snippet = FacultyResource.objects.create(
            heading='Outstanding slides', description='<p>x</p>', unlocked_resource=True,
            locale=outstanding_book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=outstanding_book, resource=outstanding_snippet,
            link_external='https://x.co', remediation_status='in_progress')
        # untracked_book has no remediation_status anywhere — must not read as "clear".
        result = resolve_books({
            'subject': None, 'book_state': 'live', 'order': 'title', 'limit': 10,
            'remediation': 'clear',
            'columns': [{'field': 'title', 'header': '', 'type': ''}],
        })
        titles = {r['cells'][0]['content'] for r in result['rows']}
        self.assertEqual(titles, {'University Physics'})
        self.assertNotIn('College Physics', titles)
        self.assertNotIn('Chemistry', titles)

    def test_resolve_books_remediation_outstanding_matches_book_or_resource(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_books
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            book_level = self._make_book(remediation_status='removed')
            resource_level = self._make_book(title='College Physics', slug='college-physics')
            self._make_book(title='Chemistry', slug='chemistry', remediation_status='fixed')
        snippet = FacultyResource.objects.create(
            heading='Slides', description='<p>x</p>', unlocked_resource=True,
            locale=resource_level.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=resource_level, resource=snippet,
            link_external='https://x.co', remediation_status='deprecated')
        result = resolve_books({
            'subject': None, 'book_state': 'live', 'order': 'title', 'limit': 10,
            'remediation': 'outstanding',
            'columns': [{'field': 'title', 'header': '', 'type': ''}],
        })
        titles = {r['cells'][0]['content'] for r in result['rows']}
        self.assertEqual(titles, {'University Physics', 'College Physics'})


class NewsSourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import datetime
        from news.models import NewsIndex, NewsArticle
        root_page = Page.objects.get(title="Root")
        news_index = NewsIndex(title="News")
        root_page.add_child(instance=news_index)
        for i, (heading, date) in enumerate([
            ('Older post', datetime.date(2026, 1, 1)),
            ('Newer post', datetime.date(2026, 6, 1)),
        ]):
            article = NewsArticle(title=heading, slug=f'post-{i}',
                                  heading=heading, subheading='sub',
                                  author='OpenStax', date=date,
                                  body='[]')
            news_index.add_child(instance=article)

    def test_resolve_news_orders_newest_first_by_default(self):
        from pages.table_sources import resolve_news
        result = resolve_news({
            'subject': '', 'tag': '', 'order': '', 'limit': 10,
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'date', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'Newer post')
        self.assertEqual(result['rows'][0]['cells'][1]['content'], '06/01/2026')

    def test_resolve_news_heading_link_builds_blog_url(self):
        from pages.table_sources import resolve_news
        result = resolve_news({
            'subject': '', 'tag': '', 'order': '', 'limit': 10,
            'columns': [{'field': 'heading_link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['target']['value'], '/blog/post-1')
        self.assertEqual(cta['target']['type'], 'internal')

    def test_resolve_news_respects_limit(self):
        from pages.table_sources import resolve_news
        result = resolve_news({
            'subject': '', 'tag': '', 'order': '', 'limit': 1,
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)

    def test_resolve_news_subject_filter_selects_matching_articles(self):
        import json
        from news.models import NewsArticle
        from snippets.models import Subject
        from wagtail.models import Locale
        science = Subject.objects.create(name='Science', locale=Locale.get_default())
        # Real StreamField shape: SubjectBlock's chooser stores the Subject
        # snippet's ID (see NewsArticle.blog_subjects / search_subject_names).
        NewsArticle.objects.filter(slug='post-1').update(article_subjects=json.dumps([{
            'type': 'subject',
            'value': [{'type': 'item', 'value': {'subject': science.id, 'featured': False}}],
        }]))
        article = NewsArticle.objects.get(slug='post-1')
        self.assertEqual(article.search_subject_names(), 'Science')  # guards fixture shape

        from pages.table_sources import resolve_news
        result = resolve_news({
            'subject': 'Science', 'tag': '', 'order': '', 'limit': 10,
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'Newer post')

    def test_resolve_news_tag_filter_selects_matching_articles(self):
        from news.models import NewsArticle
        from pages.table_sources import resolve_news
        article = NewsArticle.objects.get(slug='post-1')  # 'Newer post'
        article.tags.add('featured')
        article.save()  # ClusterTaggableManager defers writes until save()

        result = resolve_news({
            'subject': '', 'tag': 'featured', 'order': '', 'limit': 10,
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'Newer post')


class BookResourcesSourceTests(BooksSourceTests):
    # Inherits setUpTestData (homepage/BookIndex/site/doc) from BooksSourceTests.

    def _add_video(self, book, **overrides):
        from books.models import VideoFacultyResources
        data = dict(book_video_faculty_resource=book, resource_heading='Interface',
                    resource_description='<p>How to use it.</p>')
        data.update(overrides)
        return VideoFacultyResources.objects.create(**data)

    def _make_book_with_resources(self):
        from books.models import BookFacultyResources, BookStudentResources
        from snippets.models import FacultyResource, StudentResource
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        faculty_snippet = FacultyResource.objects.create(
            heading='Instructor Getting Started Guide',
            description='<p>Start here.</p>', unlocked_resource=True,
            locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=faculty_snippet,
            link_external='https://example.com/guide.pdf',
            link_text='Download guide', display_on_k12=True)
        student_snippet = StudentResource.objects.create(
            heading='Student Solution Manual',
            description='<p>Solutions.</p>', unlocked_resource=True,
            locale=book.locale)
        BookStudentResources.objects.create(
            book_student_resource=book, resource=student_snippet,
            link_external='https://example.com/solutions.pdf',
            link_text='Download solutions')
        return book

    def test_resolve_instructor_resources(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'link', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'],
                         'Instructor Getting Started Guide')
        cta = result['rows'][0]['cells'][1]['cta'][0]
        self.assertEqual(cta['text'], 'Download guide')
        self.assertEqual(cta['target']['value'], 'https://example.com/guide.pdf')

    def test_resolve_student_resources(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'student', 'audience': '',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'],
                         'Student Solution Manual')

    def test_k12_audience_filters_unflagged_resources(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        instructor = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': 'k12',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(instructor['rows']), 1)  # flagged display_on_k12
        student = resolve_book_resources({
            'books': [book], 'resource_type': 'student', 'audience': 'k12',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(student['rows'], [])  # not flagged

    def test_resource_category_filters_rows(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        FacultyResource.objects.filter(heading='Instructor Getting Started Guide').update(
            resource_category='Getting Started')
        other_snippet = FacultyResource.objects.create(
            heading='Instructor PowerPoint Slides',
            description='<p>Slides.</p>', unlocked_resource=True,
            locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=other_snippet,
            link_external='https://example.com/slides.pdf',
            link_text='Download slides')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'resource_category': ' Getting Started ',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['cells'][0]['content'],
                         'Instructor Getting Started Guide')

    def test_resource_category_choices_lists_populated_values(self):
        from snippets.models import FacultyResource, StudentResource
        from pages.table_block import resource_category_choices
        book = self._make_book_with_resources()
        FacultyResource.objects.filter(heading='Instructor Getting Started Guide').update(
            resource_category='Getting Started')
        StudentResource.objects.create(
            heading='Student Slides', description='<p>x</p>',
            unlocked_resource=True, resource_category='Slides',
            locale=book.locale)
        self.assertEqual(resource_category_choices(),
                         [('Getting Started', 'Getting Started'), ('Slides', 'Slides')])

    def test_resource_link_precedence_external_over_document(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        snippet = FacultyResource.objects.create(
            heading='Both Links', description='<p>x</p>', unlocked_resource=True,
            locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=snippet,
            link_external='https://example.com/wins.pdf',
            link_document=self.test_doc, link_text='Get it')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['target']['value'], 'https://example.com/wins.pdf')
        self.assertEqual(cta['target']['type'], 'external')

    def test_resource_page_link_is_internal_relative(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        snippet = FacultyResource.objects.create(
            heading='Page Link', description='<p>x</p>', unlocked_resource=True,
            locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=snippet,
            link_page=self.book_index, link_text='Browse')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertTrue(cta['target']['value'].startswith('/'),
                        cta['target']['value'])
        self.assertEqual(cta['target']['type'], 'internal')

    def test_description_renders_expanded_html_not_raw_tags(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        # Internal page link in stored richtext form; expand_db_html turns it
        # into a real href (raw tags/linktype would be broken output).
        snippet = FacultyResource.objects.create(
            heading='Guide',
            description=f'<p>See <a linktype="page" id="{self.book_index.id}">here</a>.</p>',
            unlocked_resource=True, locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=snippet, link_external='https://x.co')
        # Column type set to Text must NOT escape a rich-text field.
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'description', 'header': '', 'type': 'text'}],
        })
        content = result['rows'][0]['cells'][0]['content']
        self.assertNotIn('&lt;p', content)          # not escaped to visible tags (with or without attrs)
        self.assertNotIn('linktype', content)       # link was expanded
        self.assertIn('href=', content)

    def test_book_column_lists_book_title(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'book', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'University Physics')

    def test_same_resource_different_links_get_separate_rows(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        # Both books share the default salesforce_book_id, so the SF lookup
        # fires twice against the one recorded interaction — allow the replay.
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            book_a = self._make_book()
            book_b = self._make_book(title='College Physics', slug='college-physics')
        shared = FacultyResource.objects.create(
            heading='PowerPoint Slides', description='<p>x</p>',
            unlocked_resource=True, locale=book_a.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book_a, resource=shared,
            link_external='https://example.com/a.pdf')
        BookFacultyResources.objects.create(
            book_faculty_resource=book_b, resource=shared,
            link_external='https://example.com/b.pdf')
        result = resolve_book_resources({
            'books': [book_a, book_b], 'resource_type': 'instructor', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'book', 'header': '', 'type': ''},
                {'field': 'link', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(len(result['rows']), 2)  # distinct files, not merged
        books_seen = [row['cells'][1]['content'] for row in result['rows']]
        self.assertEqual(books_seen, ['University Physics', 'College Physics'])
        links_seen = [row['cells'][2]['cta'][0]['target']['value'] for row in result['rows']]
        self.assertEqual(links_seen,
                         ['https://example.com/a.pdf', 'https://example.com/b.pdf'])

    def test_same_resource_same_link_stays_one_row(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            book_a = self._make_book()
            book_b = self._make_book(title='College Physics', slug='college-physics')
        shared = FacultyResource.objects.create(
            heading='Instructor Getting Started Guide', description='<p>x</p>',
            unlocked_resource=True, locale=book_a.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book_a, resource=shared,
            link_external='https://example.com/guide.pdf')
        BookFacultyResources.objects.create(
            book_faculty_resource=book_b, resource=shared,
            link_external='https://example.com/guide.pdf')
        result = resolve_book_resources({
            'books': [book_a, book_b], 'resource_type': 'instructor', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'book', 'header': '', 'type': ''},
                {'field': 'link', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(len(result['rows']), 1)  # same file, one row
        self.assertEqual(result['rows'][0]['cells'][1]['content'],
                         'University Physics, College Physics')
        cta = result['rows'][0]['cells'][2]['cta'][0]
        self.assertEqual(cta['target']['value'], 'https://example.com/guide.pdf')

    def test_resource_category_column(self):
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        FacultyResource.objects.filter(heading='Instructor Getting Started Guide').update(
            resource_category='Getting Started')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'resource_category', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'Getting Started')

    def test_all_books_when_no_books_or_filters(self):
        # No manual books and no subject filters => every listed book's resources.
        from pages.table_sources import resolve_book_resources
        self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'],
                         'Instructor Getting Started Guide')

    def test_he_subject_filter_selects_matching_books(self):
        from books.models import BookSubjects
        from snippets.models import Subject
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        science = Subject.objects.create(name='Science', locale=book.locale)
        arts = Subject.objects.create(name='Arts', locale=book.locale)
        BookSubjects.objects.create(book_subject=book, subject=science)

        cols = [{'field': 'heading', 'header': '', 'type': ''}]
        matched = resolve_book_resources({
            'books': [], 'subject': science, 'resource_type': 'instructor', 'columns': cols})
        self.assertEqual([r['cells'][0]['content'] for r in matched['rows']],
                         ['Instructor Getting Started Guide'])
        # A subject the book isn't in returns nothing.
        missed = resolve_book_resources({
            'books': [], 'subject': arts, 'resource_type': 'instructor', 'columns': cols})
        self.assertEqual(missed['rows'], [])

    def test_k12_subject_filter_selects_matching_books(self):
        from books.models import K12BookSubjects
        from snippets.models import K12Subject
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        k12 = K12Subject.objects.create(name='High School Physics',
                                        subject_category='Science', locale=book.locale)
        K12BookSubjects.objects.create(k12book_subject=book, subject=k12)

        result = resolve_book_resources({
            'books': [], 'k12_subject': k12, 'resource_type': 'instructor',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual([r['cells'][0]['content'] for r in result['rows']],
                         ['Instructor Getting Started Guide'])

    def test_manual_books_take_precedence_over_filters(self):
        # A stray subject filter is ignored when specific books are chosen.
        from snippets.models import Subject
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        unrelated = Subject.objects.create(name='Nowhere', locale=book.locale)
        result = resolve_book_resources({
            'books': [book], 'subject': unrelated, 'resource_type': 'instructor',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)

    def test_omitting_new_config_keys_matches_pre_change_shape(self):
        # Regression: a config dict saved before this feature has no
        # resource_type='all', 'remediation', or 'include_web_pdf' keys at all.
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'book', 'header': '', 'type': ''},
                {'field': 'link', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(len(result['rows']), 1)  # no Web PDF row snuck in
        self.assertEqual(result['rows'][0]['cells'][0]['content'],
                         'Instructor Getting Started Guide')
        self.assertEqual(result['rows'][0]['cells'][1]['content'], 'University Physics')
        self.assertEqual(result['rows'][0]['cells'][2]['cta'][0]['target']['value'],
                         'https://example.com/guide.pdf')

    def test_remediation_status_column_and_blank_status_renders_empty(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        tracked = FacultyResource.objects.create(
            heading='Tracked', description='<p>x</p>', unlocked_resource=True,
            locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=tracked, link_external='https://x.co',
            remediation_status='fixed')
        untracked = FacultyResource.objects.create(
            heading='Untracked', description='<p>x</p>', unlocked_resource=True,
            locale=book.locale)
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=untracked, link_external='https://y.co')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'remediation_status', 'header': '', 'type': ''},
            ],
        })
        rows = {r['cells'][0]['content']: r['cells'][1]['content'] for r in result['rows']}
        self.assertEqual(rows['Tracked'], 'Fixed (remediated)')
        self.assertEqual(rows['Untracked'], '')

    def test_resource_type_all_returns_both_instructor_and_student_tagged(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'all', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'resource_type', 'header': '', 'type': ''},
            ],
        })
        tags = {r['cells'][0]['content']: r['cells'][1]['content'] for r in result['rows']}
        self.assertEqual(tags, {
            'Instructor Getting Started Guide': 'Instructor',
            'Student Solution Manual': 'Student',
        })

    def test_remediation_outstanding_filter_excludes_fixed_na_and_blank(self):
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        for status in ['fixed', 'in_progress', 'deprecated', 'removed', 'na', '']:
            snippet = FacultyResource.objects.create(
                heading=f'R-{status or "blank"}', description='<p>x</p>',
                unlocked_resource=True, locale=book.locale)
            BookFacultyResources.objects.create(
                book_faculty_resource=book, resource=snippet, link_external='https://x.co',
                remediation_status=status)
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'remediation': 'outstanding',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        headings = {r['cells'][0]['content'] for r in result['rows']}
        self.assertEqual(headings, {'R-in_progress', 'R-deprecated', 'R-removed'})

    def test_include_web_pdf_emits_one_row_per_book_with_book_status(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        book.remediation_status = 'deprecated'
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            book.save()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'include_web_pdf': True,
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'remediation_status', 'header': '', 'type': ''},
                {'field': 'resource_type', 'header': '', 'type': ''},
            ],
        })
        web_pdf_rows = [r for r in result['rows'] if r['cells'][0]['content'] == 'Web PDF']
        self.assertEqual(len(web_pdf_rows), 1)
        self.assertEqual(web_pdf_rows[0]['cells'][1]['content'], 'Deprecated (temporarily removed)')
        self.assertEqual(web_pdf_rows[0]['cells'][2]['content'], 'Book')

    def test_include_web_pdf_respects_remediation_filter(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        book.remediation_status = 'fixed'  # not outstanding
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            book.save()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'include_web_pdf': True, 'remediation': 'outstanding',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertNotIn('Web PDF', [r['cells'][0]['content'] for r in result['rows']])

    def test_locked_resource_link_points_at_book_page_no_real_url_leaks(self):
        # No request/user reaches this resolver and its output is cached for
        # 30 days for every visitor, so a locked resource's real file URL must
        # never be baked into the cell — point at the book detail page, where
        # the existing resource box applies the gate with a working return path.
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        locked_snippet = FacultyResource.objects.create(
            heading='Locked Guide', description='<p>x</p>', locale=book.locale)  # unlocked_resource default False
        row = BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=locked_snippet,
            link_document=self.test_doc, link_text='Download')
        real_url = row.link_document_url
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cell = result['rows'][0]['cells'][0]
        cta = cell['cta'][0]
        self.assertEqual(cta['text'], 'View on book page')
        self.assertEqual(cta['target']['value'],
                         f'/details/books/{book.slug}?Instructor%20resources')
        serialized = json.dumps(cell)
        self.assertNotIn(real_url, serialized)
        self.assertNotIn('Download', serialized)  # original CTA text must not leak either

    def test_locked_student_resource_links_to_student_tab(self):
        # The book page picks its tab from a bare query-string key matching the
        # tab label, so a student row must not send readers to the instructor tab.
        from books.models import BookStudentResources
        from snippets.models import StudentResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        locked = StudentResource.objects.create(
            heading='Locked Student Guide', description='<p>x</p>',
            locale=book.locale, unlocked_resource=False)
        BookStudentResources.objects.create(
            book_student_resource=book, resource=locked,
            link_external='https://example.com/secret.pdf')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'student', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['target']['value'],
                         f'/details/books/{book.slug}?Student%20resources')
        self.assertNotIn('secret.pdf', json.dumps(result['rows'][0]))

    def test_book_slugs_stay_aligned_with_titles_when_row_shared(self):
        # A resource shared across books merges into one row listing both books;
        # _book_slugs must track _book_titles so the link targets a real book.
        from books.models import BookFacultyResources
        from snippets.models import FacultyResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml',
                              allow_playback_repeats=True):
            book_a = self._make_book()
            book_b = self._make_book(title='College Physics', slug='college-physics')
        shared = FacultyResource.objects.create(
            heading='Shared Guide', description='<p>x</p>', locale=book_a.locale)
        for b in (book_a, book_b):
            BookFacultyResources.objects.create(
                book_faculty_resource=b, resource=shared, link_external='https://example.com/s.pdf')
        result = resolve_book_resources({
            'books': [book_a, book_b], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'book', 'header': '', 'type': ''},
                        {'field': 'link', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)
        books_cell, link_cell = result['rows'][0]['cells']
        self.assertIn(book_a.title, books_cell['content'])
        self.assertIn(book_b.title, books_cell['content'])
        # First listed book wins the link, matching the first listed title.
        self.assertEqual(link_cell['cta'][0]['target']['value'],
                         f'/details/books/{book_a.slug}?Instructor%20resources')

    def test_resource_fk_none_fails_closed_no_link(self):
        # resource is nullable (SET_NULL) — treat a null FK as locked, not
        # unlocked, since there's no unlocked_resource flag to check.
        from books.models import BookFacultyResources
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        BookFacultyResources.objects.create(
            book_faculty_resource=book, resource=None,
            link_external='https://example.com/secret.pdf', link_text='Download')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cell = result['rows'][0]['cells'][0]
        self.assertEqual(cell['cta'][0]['text'], 'View on book page')
        self.assertNotIn('secret.pdf', json.dumps(cell))

    def test_student_resource_default_unlocked_emits_real_link(self):
        # Regression guard for the live Student Resource Hub page (id 987):
        # StudentResource.unlocked_resource defaults True, so its links must
        # keep working without any explicit override.
        from books.models import BookStudentResources
        from snippets.models import StudentResource
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        snippet = StudentResource.objects.create(
            heading='Study Guide', description='<p>x</p>', locale=book.locale)
        BookStudentResources.objects.create(
            book_student_resource=book, resource=snippet,
            link_external='https://example.com/study.pdf', link_text='Get it')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'student', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['text'], 'Get it')
        self.assertEqual(cta['target']['value'], 'https://example.com/study.pdf')

    def test_web_pdf_row_link_is_public_not_gated(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'instructor', 'audience': '',
            'include_web_pdf': True,
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'link', 'header': '', 'type': ''},
            ],
        })
        web_pdf = next(r for r in result['rows'] if r['cells'][0]['content'] == 'Web PDF')
        self.assertEqual(web_pdf['cells'][1]['cta'], [])
        self.assertEqual(web_pdf['cells'][1]['content'], 'View resource')

    def test_video_resource_remediation_status_renders_display_label(self):
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        self._add_video(book, resource_heading='Alto', remediation_status='fixed')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'video', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'remediation_status', 'header': '', 'type': ''},
            ],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'], 'Alto')
        self.assertEqual(result['rows'][0]['cells'][1]['content'], 'Fixed (remediated)')

    def test_resource_type_video_returns_only_video_rows(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        self._add_video(book, resource_heading='Evernote')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'video', 'audience': '',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual([r['cells'][0]['content'] for r in result['rows']], ['Evernote'])

    def test_resource_type_all_includes_instructor_student_and_video(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        self._add_video(book, resource_heading='Google Home')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'all', 'audience': '',
            'columns': [
                {'field': 'heading', 'header': '', 'type': ''},
                {'field': 'resource_type', 'header': '', 'type': ''},
            ],
        })
        tags = {r['cells'][0]['content']: r['cells'][1]['content'] for r in result['rows']}
        self.assertEqual(tags, {
            'Instructor Getting Started Guide': 'Instructor',
            'Student Solution Manual': 'Student',
            'Google Home': 'Videos',
        })

    def test_video_row_with_video_url_emits_real_link_not_login_prompt(self):
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        self._add_video(book, resource_heading='Concept Trailers',
                        video_title='Watch now', video_url='https://example.com/watch')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'video', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cell = result['rows'][0]['cells'][0]
        cta = cell['cta'][0]
        self.assertEqual(cta['text'], 'Watch now')
        self.assertEqual(cta['target']['value'], 'https://example.com/watch')
        self.assertNotIn('View on book page', json.dumps(cell))

    def test_video_row_with_no_link_field_emits_empty_link_not_login_prompt(self):
        # Video ancillaries are public and have no `resource` FK to check —
        # a video row with neither video_url nor video_file set must not be
        # wrongly gated into the book-page fallback (the fail-closed
        # path _resource_link_cell uses for real, access-gated resources).
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        self._add_video(book, resource_heading='Video Series')
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'video', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cell = result['rows'][0]['cells'][0]
        self.assertEqual(cell['cta'], [])
        self.assertNotIn('View on book page', cell['content'])

    def test_video_remediation_outstanding_filter_applies_to_video_rows(self):
        from pages.table_sources import resolve_book_resources
        with vcr.use_cassette('fixtures/vcr_cassettes/books_univ_physics.yaml'):
            book = self._make_book()
        for status in ['fixed', 'in_progress', 'deprecated', 'removed', 'na', '']:
            self._add_video(book, resource_heading=f'V-{status or "blank"}',
                            remediation_status=status)
        result = resolve_book_resources({
            'books': [book], 'resource_type': 'video', 'audience': '',
            'remediation': 'outstanding',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        headings = {r['cells'][0]['content'] for r in result['rows']}
        self.assertEqual(headings, {'V-in_progress', 'V-deprecated', 'V-removed'})


class SubjectsSourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from wagtail.models import Locale
        from snippets.models import Subject, K12Subject
        locale = Locale.get_default()
        Subject.objects.create(name='Math', locale=locale)
        Subject.objects.create(name='Science', locale=locale)
        K12Subject.objects.create(name='Algebra', subject_category='Math',
                                  subject_link='/k12/algebra', locale=locale)
        K12Subject.objects.create(name='Biology', subject_category='Science',
                                  subject_link='/k12/biology', locale=locale)

    def test_resolve_he_subjects_sorted_by_name(self):
        from pages.table_sources import resolve_subjects
        result = resolve_subjects({
            'variant': 'he', 'k12_category': '',
            'columns': [{'field': 'name', 'header': '', 'type': ''}],
        })
        names = [r['cells'][0]['content'] for r in result['rows']]
        self.assertEqual(names, ['Math', 'Science'])

    def test_resolve_k12_subjects_filters_category_and_links(self):
        from pages.table_sources import resolve_subjects
        result = resolve_subjects({
            'variant': 'k12', 'k12_category': 'Math',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(result['rows']), 1)
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertEqual(cta['text'], 'Algebra')
        self.assertEqual(cta['target']['value'], '/k12/algebra')


class EndpointSourceTests(BooksSourceTests):
    # Inherits setUpTestData (homepage/BookIndex/site/doc) from BooksSourceTests
    # so the Wagtail pages API root has a site whose root page serves pages.

    def test_rejects_paths_outside_cms_api(self):
        from pages.table_sources import resolve_endpoint
        for bad in ['/admin/', 'https://openstax.org/apps/cms/api/v2/pages/',
                    '/apps/other/', '//evil.com/apps/cms/api/']:
            with self.assertRaises(ValueError):
                resolve_endpoint({'path': bad, 'items_key': 'items', 'columns': []})

    def test_resolves_wagtail_pages_api_and_maps_dotted_fields(self):
        from pages.table_sources import resolve_endpoint
        # The Wagtail pages API root always serves the Root page in tests.
        result = resolve_endpoint({
            'path': '/apps/cms/api/v2/pages/?limit=5',
            'items_key': 'items',
            'columns': [
                {'field': 'title', 'header': 'Page', 'type': ''},
                {'field': 'meta.type', 'header': 'Type', 'type': ''},
            ],
        })
        self.assertEqual(result['columns'][0], {'header': 'Page', 'type': 'text'})
        self.assertTrue(result['rows'])
        self.assertTrue(result['rows'][0]['cells'][1]['content'])  # meta.type resolved

    def test_missing_field_yields_empty_cell(self):
        from pages.table_sources import resolve_endpoint
        result = resolve_endpoint({
            'path': '/apps/cms/api/v2/pages/?limit=1',
            'items_key': 'items',
            'columns': [{'field': 'no.such.key', 'header': 'X', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0], {'content': '', 'cta': []})

    def test_nonexistent_resource_raises_value_error(self):
        from pages.table_sources import resolve_endpoint
        with self.assertRaises(ValueError):
            resolve_endpoint({'path': '/apps/cms/api/books/definitely-does-not-exist-xyz/',
                              'items_key': 'items', 'columns': []})

    def test_malformed_subpath_raises_value_error(self):
        from pages.table_sources import resolve_endpoint
        with self.assertRaises(ValueError):
            resolve_endpoint({'path': '/apps/cms/api/../../admin/',
                              'items_key': 'items', 'columns': []})

    def test_bare_list_payload_with_items_key_raises_value_error(self):
        from pages.table_sources import resolve_endpoint
        # snippets/roles/ is an unpaginated DRF list view: bare JSON list.
        with self.assertRaises(ValueError):
            resolve_endpoint({'path': '/apps/cms/api/snippets/roles/',
                              'items_key': 'items', 'columns': []})
