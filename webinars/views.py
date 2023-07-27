from rest_framework import viewsets

from .models import Webinar, webinar_subject_search, webinar_collection_search
from .serializers import WebinarSerializer
from .search import search


class WebinarViewSet(viewsets.ModelViewSet):
    serializer_class = WebinarSerializer

    def get_queryset(self):
        queryset = Webinar.objects.all().order_by('-start')
        subject = self.request.query_params.get('subject', None)
        collection = self.request.query_params.get('collection', None)
        q = self.request.query_params.get('q', None)
        if q is not None:
            return search(q)
        elif subject is not None:
            queryset = webinar_subject_search(subject)
        elif collection is not None:
            queryset = webinar_collection_search(collection)
        return queryset
