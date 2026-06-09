from django.test import TestCase

from django_ai_core.contrib.index import registry


class RelatedPagesTests(TestCase):
    def test_page_vector_index_registered(self):
        self.assertIsNotNone(registry.get("PageVectorIndex"))

    def test_relation_models_target_their_pages(self):
        from books.models import Book, BookRelatedPage
        from news.models import NewsArticle, NewsArticleRelatedPage
        from pages.models import FlexPage, FlexPageRelatedPage

        for through, page_model in [
            (NewsArticleRelatedPage, NewsArticle),
            (BookRelatedPage, Book),
            (FlexPageRelatedPage, FlexPage),
        ]:
            self.assertIs(through._meta.get_field("page").related_model, page_model)
            self.assertEqual(
                through._meta.get_field("related_page").related_model.__name__, "Page"
            )

    def test_pages_expose_related_pages_accessor(self):
        from news.models import NewsArticle

        self.assertTrue(hasattr(NewsArticle, "related_pages"))
