from rest_framework import viewsets

from .models import Webinar, webinar_subject_search
from .serializers import WebinarSerializer


class WebinarViewSet(viewsets.ModelViewSet):
    serializer_class = WebinarSerializer

    def get_queryset(self):
        queryset = Webinar.objects.all()
        subject = self.request.query_params.get('subject', None)
        if subject is not None:
            queryset = webinar_subject_search(subject)
        return queryset