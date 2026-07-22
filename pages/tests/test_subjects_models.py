from types import SimpleNamespace
from django.test import TestCase
from unittest.mock import MagicMock, patch

from pages.models.subjects import Subject, Subjects


class _ChainableList(list):
    def exclude(self, **kwargs):
        return self

    def prefetch_related(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def distinct(self):
        return self


class _FakeBook:
    def __init__(self):
        self.id = 1
        self.slug = "fake-book"
        self.book_state = "live"
        self.title = "Fake Book"
        self.subject_categories = ["Algebra"]
        self.is_ap = False
        self.cover_url = "https://example.com/cover.png"
        self.cover_color = "blue"
        self.pdf_url = "https://example.com/book.pdf"
        self.webview_link = "https://example.com/webview"
        self.webview_rex_link = "https://example.com/rex"
        self.bookshare_link = ""
        self.amazon_coming_soon = False
        self.amazon_link = ""
        self.bookstore_coming_soon = False
        self.salesforce_abbreviation = ""
        self.salesforce_name = ""
        self.last_updated_pdf = ""

    def subjects(self):
        return ["Math"]

    def k12subjects(self):
        return []

    def book_urls(self):
        return []


class SubjectsModelTests(TestCase):
    def test_subjects_property_batches_subject_category_queries(self):
        subject1 = SimpleNamespace(id=1, name="Math", subject_icon="math-icon")
        subject2 = SimpleNamespace(id=2, name="Science", subject_icon="science-icon")
        category1 = SimpleNamespace(subject_id=1, subject_category="Algebra")
        category2 = SimpleNamespace(subject_id=2, subject_category="Biology")

        subjects_qs = MagicMock()
        subjects_qs.order_by.return_value = [subject1, subject2]
        categories_qs = MagicMock()
        categories_qs.order_by.return_value = [category1, category2]

        with patch("pages.models.subjects.snippets.Subject.objects.filter", return_value=subjects_qs) as subject_filter:
            with patch("pages.models.subjects.snippets.SubjectCategory.objects.filter", return_value=categories_qs) as category_filter:
                page = SimpleNamespace(locale="en")
                result = Subjects.subjects.fget(page)

        subject_filter.assert_called_once_with(locale="en")
        category_filter.assert_called_once_with(subject_id__in=[1, 2])
        self.assertEqual(result["Math"]["categories"], ["Algebra"])
        self.assertEqual(result["Science"]["categories"], ["Biology"])

    def test_subject_property_batches_category_queries_and_filters_books(self):
        selected_subject = SimpleNamespace(id=10, name="Math", subject_icon="math-icon")
        category = SimpleNamespace(subject_id=10, subject_category="Algebra", description="desc")
        mock_books = _ChainableList([_FakeBook()])

        categories_qs = MagicMock()
        categories_qs.order_by.return_value = [category]

        with patch("pages.models.subjects.snippets.Subject.objects.filter", return_value=[selected_subject]):
            with patch("pages.models.subjects.snippets.SubjectCategory.objects.filter", return_value=categories_qs) as category_filter:
                with patch("pages.models.subjects.Book.objects.filter", return_value=mock_books) as book_filter:
                    page = SimpleNamespace(locale="en", selected_subject=[SimpleNamespace(subject_name="Math")])
                    result = Subject.subjects.fget(page)

        category_filter.assert_called_once_with(subject_id__in=[10])
        book_filter.assert_called_once_with(book_subjects__subject=selected_subject)
        self.assertIn("Algebra", result["Math"]["categories"])
        self.assertIn("Fake Book", result["Math"]["categories"]["Algebra"]["books"])
