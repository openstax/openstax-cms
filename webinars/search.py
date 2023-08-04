import re

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.http import JsonResponse

from webinars.models import Webinar


def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
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
    found_entries = []

    # search by keyword
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        vector = SearchVector('title', weight='A') + SearchVector('description', weight='A') + SearchVector(
            'speakers', weight='B')
        query = get_query(query_string)

        found_entries = Webinar.objects.annotate(
            rank=SearchRank(vector, query),
            search=vector,
        ).filter(rank__gte=0.3).order_by('-start', 'rank')

    search_results_json = []
    for result in found_entries:
        search_results_json.append({
            'id': result.id,
            'title': result.title,
            'description': result.description,
            'start': result.start,
            'end': result.end,
            'speakers': result.speakers,
            'spaces_remaining': result.spaces_remaining,
            'registration_url': result.registration_url,
            'registration_link_text': result.registration_link_text,
            'display_on_tutor_page': result.display_on_tutor_page,
            'subjects': result.selected_subjects,
            'collections': result.selected_collections,
        })
    return JsonResponse(search_results_json, safe=False)

