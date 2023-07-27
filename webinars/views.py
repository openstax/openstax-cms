from rest_framework import viewsets

from .models import Webinar, webinar_subject_search, webinar_collection_search
from .serializers import WebinarSerializer


class WebinarViewSet(viewsets.ModelViewSet):
    serializer_class = WebinarSerializer

    def get_queryset(self):
        queryset = Webinar.objects.all().order_by('-start')
        subject = self.request.query_params.get('subject', None)
        collection = self.request.query_params.get('collection', None)
        if subject is not None:
            queryset = webinar_subject_search(subject)
        elif collection is not None:
            queryset = webinar_collection_search(collection)
        return queryset
