import re

from django.http import JsonResponse

from news.models import NewsArticle

# The Postgres backend nests one expression per whitespace/hyphen-separated
# term, and Django recurses that tree when hashing it — past ~150 terms a query
# raises RecursionError instead of returning results.
MAX_SEARCH_TERMS = 25


def _csv_param(request, name):
    raw = request.GET.get(name, '').strip()
    return [v.strip() for v in raw.split(',') if v.strip()]


def _live_articles():
    return NewsArticle.objects.live() \
        .select_related('featured_image') \
        .prefetch_related('tags')


def search(request):
    q = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    subjects = _csv_param(request, 'subjects')
    collection = request.GET.get('collection', '').strip()
    content_types = _csv_param(request, 'types')
    sort = request.GET.get('sort', 'relevance').strip()
    q = ' '.join(
        token for token in re.split(r'[\s\-]+', q)[:MAX_SEARCH_TERMS] if token
    )

    if q:
        results = _live_articles().search(q)
    elif tag:
        results = _live_articles().filter(
            tags__name__in=[tag]
        ).order_by('-date').distinct()
    else:
        results = _live_articles().order_by('-date')

    articles = list(results)
    if subjects:
        articles = [a for a in articles
                    if set(subjects) & {s['name'] for s in a.blog_subjects}]
    if collection:
        articles = [a for a in articles
                    if collection in {c['name'] for c in a.blog_collections}]
    if content_types:
        articles = [a for a in articles
                    if set(content_types) & set(a.blog_content_types)]

    if q and sort == 'newest':
        articles.sort(key=lambda a: a.date, reverse=True)

    search_results_json = []
    search_results_shown = set()
    for result in articles:
        if result.slug in search_results_shown:
            continue

        search_results_shown.add(result.slug)

        search_results_json.append({
            'id': result.id,
            'title': result.title,
            'subheading': result.subheading,
            'body_blurb': result.body_blurb,
            'article_image': result.article_image,
            'article_image_alt': result.featured_image_alt_text,
            'date': result.date,
            'author': result.author,
            'pin_to_top': result.pin_to_top,
            'tags': [t.name for t in result.tags.all()],
            'collections': result.blog_collections,
            'article_subjects': result.blog_subjects,
            'content_types': result.blog_content_types,
            'slug': result.slug,
            'seo_title': result.seo_title,
            'search_description': result.search_description,
        })
    return JsonResponse(search_results_json, safe=False)
