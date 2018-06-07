import django_filters
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from .models import Errata
from .serializers import ErrataSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class ErrataFilter(FilterSet):
    book_title = django_filters.CharFilter(name='book__title')
    book_id = django_filters.CharFilter(name='book__id')

    class Meta:
        model = Errata
        fields = ['book_title', 'book_id', 'archived']


class ErrataView(ModelViewSet):
    queryset = Errata.objects.filter(archived=False).filter(is_assessment_errata='No')
    serializer_class = ErrataSerializer
    http_method_names = ['get', 'post', 'head']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ErrataFilter
    ordering_fields = ('id', 'resolution_date', 'created', 'modified', )
