from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .registry import SOURCES


class SourcePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


def _requested_page(params):
    try:
        return int(params.get('page', 1))
    except ValueError:
        return 1


def _paginated(source, params, request):
    paginator = SourcePagination()
    results = source.build_results(params)
    try:
        page = paginator.paginate_queryset(results, request)
    except NotFound:
        # Sources are paginated independently off one shared `page`, so the
        # shortest one runs out first; that must not 404 the whole envelope.
        return {
            'page': _requested_page(params),
            'page_size': paginator.get_page_size(request),
            'total': results.count(),
            'next': None,
            'previous': None,
            'results': [],
        }
    return {
        'page': paginator.page.number,
        'page_size': paginator.get_page_size(request),
        'total': paginator.page.paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'results': [source.to_dict(obj) for obj in page],
    }


class SearchView(APIView):
    def get(self, request):
        params = request.query_params
        requested = [key.strip() for key in params.get('sources', '').split(',') if key.strip()]
        keys = requested or list(SOURCES)
        return Response({
            'query': params.get('q', '').strip(),
            'sources': {
                key: _paginated(SOURCES[key], params, request)
                for key in keys if key in SOURCES
            },
        })
