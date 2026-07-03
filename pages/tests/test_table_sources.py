import datetime

import vcr
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

    def test_date_cell_non_date_fallback_is_escaped(self):
        cell = build_cell('<b>not a date</b>', 'date')
        self.assertNotIn('<b>', cell['content'])
        self.assertIn('&lt;b&gt;', cell['content'])


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
        test_image = SimpleUploadedFile(
            name='openstax.png',
            content=open("pages/static/images/openstax.png", 'rb').read())
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


class BookResourcesSourceTests(BooksSourceTests):
    # Inherits setUpTestData (homepage/BookIndex/site/doc) from BooksSourceTests.

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
            'book': book, 'resource_type': 'instructor', 'audience': '',
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
            'book': book, 'resource_type': 'student', 'audience': '',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(result['rows'][0]['cells'][0]['content'],
                         'Student Solution Manual')

    def test_k12_audience_filters_unflagged_resources(self):
        from pages.table_sources import resolve_book_resources
        book = self._make_book_with_resources()
        instructor = resolve_book_resources({
            'book': book, 'resource_type': 'instructor', 'audience': 'k12',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(len(instructor['rows']), 1)  # flagged display_on_k12
        student = resolve_book_resources({
            'book': book, 'resource_type': 'student', 'audience': 'k12',
            'columns': [{'field': 'heading', 'header': '', 'type': ''}],
        })
        self.assertEqual(student['rows'], [])  # not flagged

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
            'book': book, 'resource_type': 'instructor', 'audience': '',
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
            'book': book, 'resource_type': 'instructor', 'audience': '',
            'columns': [{'field': 'link', 'header': '', 'type': ''}],
        })
        cta = result['rows'][0]['cells'][0]['cta'][0]
        self.assertTrue(cta['target']['value'].startswith('/'),
                        cta['target']['value'])
        self.assertEqual(cta['target']['type'], 'internal')


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
