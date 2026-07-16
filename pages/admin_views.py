from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from pages import table_sources


class TablePreviewView(APIView):
    """Staff-only: resolve a table data-source spec and return up to 5 rows,
    so editors can see what a dynamic source will render before saving the
    page. Reuses resolve_data_source directly — the same function the table
    block calls at serialize time — so the preview matches reality.
    Never 500s: resolution failures come back as {'error': message} with a
    200, so the admin widget can render them inline."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        source_type = request.data.get('source_type')
        config = request.data.get('config') or {}
        if not source_type:
            return Response({'error': 'source_type is required.'})
        try:
            data = table_sources.resolve_data_source(source_type, config)
        except KeyError:
            return Response({'error': f'Unknown source type: {source_type}'})
        except Exception as e:
            return Response({'error': str(e)})
        return Response({'columns': data['columns'], 'rows': data['rows'][:5]})
