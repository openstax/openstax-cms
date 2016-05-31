import re

from django.db.models import Q
from django.http import JsonResponse

from news.models import NewsArticle


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'body', 'heading', 'subheading',
                                               'tags__name'])

        found_entries = NewsArticle.objects.filter(entry_query).order_by('-date').distinct()

    search_results_json = []
    for result in found_entries:
        result_specific = result.specific

        search_results_json.append(dict(
            (attr, getattr(result_specific, attr))
            for attr in ['title', 'heading', 'subheading', 'body', 'id', 'pin_to_top']
            if hasattr(result_specific, attr)
        ))

    return JsonResponse(search_results_json, safe=False)
