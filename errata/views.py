import django_filters
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, MultipleChoiceFilter
from django.shortcuts import render, redirect
from .models import Errata, ERRATA_STATUS
from .serializers import ErrataSerializer
from wagtail.admin.viewsets.model import ModelViewSet as WagtailModelViewSet


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class ErrataFilter(FilterSet):
    book_title = django_filters.CharFilter(field_name='book__title')
    book_id = django_filters.CharFilter(field_name='book__id')
    is_assessment_errata__not = django_filters.CharFilter(field_name='is_assessment_errata', exclude=True)
    status__not = MultipleChoiceFilter(field_name='status', choices=ERRATA_STATUS, exclude=True)

    class Meta:
        model = Errata
        fields = ['book_title', 'book_id', 'archived', 'is_assessment_errata', 'is_assessment_errata__not', 'status__not']


class ErrataView(ModelViewSet):
    queryset = Errata.objects.prefetch_related("book")
    serializer_class = ErrataSerializer
    http_method_names = ['get', 'post', 'head']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ErrataFilter
    ordering_fields = ('id', 'resolution_date', 'created', 'modified', )

class ErrataModelViewSet(WagtailModelViewSet):
    queryset = Errata.objects.prefetch_related("book")
    model = Errata
    icon = "warning"
    list_display = ("id", "book", "created", "modified", 'status', 'error_type', 'resource')
    list_filter = ('created', "book", "status", 'archived', 'junk')
    list_export = ("id", "book", "created", "modified", 'status', 'error_type', 'resource', 'location', 'detail', 'resolution_notes')
    search_fields = ("book__title",)
    menu_label = "Errata (Beta)"
    menu_order = 9000
    add_to_admin_menu = True
    exclude_form_fields = []

errata_viewset = ErrataModelViewSet("errata")

def duplicate(errata):
    errata.pk = None
    errata.save()
    return redirect('/apps/cms/api/errata/admin/edit/{}'.format(errata.pk)) #TODO: Change to use url resolver name
