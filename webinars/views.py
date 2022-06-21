from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Webinar
from .serializers import WebinarSerializer


class WebinarViewSet(viewsets.ViewSet):
    serializer_class = WebinarSerializer

    @action(methods=['get'], detail=True)
    def list(self, request):
        queryset = Webinar.objects.all()
        subject = request.query_params.get('subject', None)
        if subject is not None:
            queryset = queryset.filter(webinar_subjects=subject)

        serializer = WebinarSerializer(queryset, many=True)
        return Response(serializer.data)
