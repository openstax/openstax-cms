import re

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.http import JsonResponse

from news.models import NewsArticle

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
    """
    Splits the query string in individual keywords, getting rid of unnecessary spaces
    and grouping quoted words together.
    
    Example Input:
    normalize_query('  some random  words "with   quotes  " and   spaces')
    
    Response:
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """

    # Remove common stopwords from the search query
    stopwords = ['of', 'is', 'a', 'at', 'is', 'the']
    querywords = query_string.split()
    resultwords = [word for word in querywords if word.lower() not in stopwords]
    result = ' '.join(resultwords)

    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(result)]


def get_query(query_string):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """

    query_items = normalize_query(query_string)

    query = SearchQuery(query_items.pop())

    for term in query_items:
        query &= SearchQuery(term)
       
    return query


def search(request):
    query_string = ''
    found_entries = []
    #filter by tags
    if ('tag' in request.GET) and request.GET['tag'].strip():
        query_string = request.GET['tag']

        found_entries = NewsArticle.objects.filter(tags__name__in=[query_string]).order_by('-date').distinct()

    #search by keyword
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        vector = SearchVector('title', weight='A') + SearchVector('subheading', weight='B') + SearchVector('author', weight='B') + SearchVector('body', weight='C') + SearchVector('tags__name', weight='C')
        query = get_query(query_string)

        found_entries = NewsArticle.objects.annotate(
            rank=SearchRank(vector, query),
            search=vector,
        ).filter(search=query).order_by('rank', '-date')

    search_results_json = []
    search_results_shown = set()
    for result in found_entries:
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
            'tags': list(result.tags.names()),
            'slug': result.slug,
            'seo_title': result.seo_title,
            'search_description': result.search_description,
        })

    return JsonResponse(search_results_json, safe=False)
    return JsonResponse([], safe=False)
