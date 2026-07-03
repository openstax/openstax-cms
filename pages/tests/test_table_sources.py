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
