from rest_framework import viewsets

from .serializers import WebinarSerializer


class WebinarViewSet(viewsets.ViewSet):
    serializer_class = WebinarSerializer

