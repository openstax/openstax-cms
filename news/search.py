import re

from django.http import JsonResponse

from news.models import NewsArticle, _cached_in_bulk
from snippets.models import Subject, BlogCollection, BlogContentType

# The Postgres backend nests one expression per whitespace/hyphen-separated
# term, and Django recurses that tree when hashing it — past ~150 terms a query
# raises RecursionError instead of returning results.
MAX_SEARCH_TERMS = 25


def _csv_param(params, name):
    raw = params.get(name, '').strip()
    return [v.strip() for v in raw.split(',') if v.strip()]


def _live_articles():
    return NewsArticle.objects.live() \
        .select_related('featured_image') \
        .prefetch_related('tags')


def _ids_for_names(model, names):
    """Resolve snippet names (as sent by the frontend) to pks, via the same
    cached in_bulk() lookup the StreamField blocks use — no extra query."""
    if not names:
        return []
    by_name = {str(obj): pk for pk, obj in _cached_in_bulk(model).items()}
    return [by_name[name] for name in names if name in by_name]


def build_news_queryset(get_params):
    """Unpaginated queryset/SearchResults for the given request params.
    `get_params` is any QueryDict-like mapping (request.GET or DRF's
    request.query_params). Facet filters are applied as real .filter() calls
    before .search() — the DB search backends fold a queryset's existing
    filters into the search query, but can't filter a SearchResults after
    the fact.
    """
    q = get_params.get('q', '').strip()
    tag = get_params.get('tag', '').strip()
    subjects = _csv_param(get_params, 'subjects')
    collection = get_params.get('collection', '').strip()
    content_types = _csv_param(get_params, 'types')
    sort = get_params.get('sort', 'relevance').strip()

    qs = _live_articles()
    if subjects:
        qs = qs.filter(subject_links__subject_id__in=_ids_for_names(Subject, subjects)).distinct()
    if collection:
        qs = qs.filter(collection_links__collection_id__in=_ids_for_names(BlogCollection, [collection])).distinct()
    if content_types:
        qs = qs.filter(content_type_links__content_type_id__in=_ids_for_names(BlogContentType, content_types)).distinct()

    if q:
        q = ' '.join(re.split(r'[\s\-]+', q)[:MAX_SEARCH_TERMS])
        if sort == 'newest':
            # date is day-granularity, so same-day articles need a real
            # tiebreaker (id) to stay stable across LIMIT/OFFSET pages.
            return qs.order_by('-date', '-id').search(q, order_by_relevance=False)
        return qs.search(q)
    if tag:
        return qs.filter(tags__name__in=[tag]).order_by('-date').distinct()
    return qs.order_by('-date')


def serialize_article(article):
    return {
        'id': article.id,
        'title': article.title,
        'subheading': article.subheading,
        'body_blurb': article.body_blurb,
        'article_image': article.article_image,
        'article_image_alt': article.featured_image_alt_text,
        'date': article.date,
        'author': article.author,
        'pin_to_top': article.pin_to_top,
        'tags': [t.name for t in article.tags.all()],
        'collections': article.blog_collections,
        'article_subjects': article.blog_subjects,
        'content_types': article.blog_content_types,
        'slug': article.slug,
        'seo_title': article.seo_title,
        'search_description': article.search_description,
    }


def search(request):
    results = build_news_queryset(request.GET)

    search_results_json = []
    search_results_shown = set()
    for result in results:
        if result.slug in search_results_shown:
            continue

        search_results_shown.add(result.slug)
        search_results_json.append(serialize_article(result))
    return JsonResponse(search_results_json, safe=False)
