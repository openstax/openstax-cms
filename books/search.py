from snippets.models import Subject

from .constants import RETIRED
from .models import Book, get_book_data


def build_book_queryset(get_params):
    """Unpaginated queryset for the given request params. Mirrors
    news.search.build_news_queryset: facet filters are applied as real
    .filter() calls before .search(), since the DB backend can't filter a
    SearchResults after the fact.
    """
    q = get_params.get('q', '').strip()
    subjects = [s.strip() for s in get_params.get('subjects', '').split(',') if s.strip()]

    qs = Book.objects.live().exclude(book_state=RETIRED)
    if subjects:
        subject_ids = Subject.objects.filter(name__in=subjects).values_list('id', flat=True)
        qs = qs.filter(book_subjects__subject_id__in=subject_ids).distinct()

    if q:
        return qs.search(q)
    return qs.order_by('title')


# Same shape used for book listings elsewhere (SubjectPage.books, BookBlock) -
# not inventing a new one for search results.
serialize_book = get_book_data
