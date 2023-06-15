import django_filters
from django.http import HttpResponse
from django.db import models
from django.contrib.auth.decorators import permission_required
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, MultipleChoiceFilter
from django.shortcuts import render, redirect
from .models import Errata, ERRATA_STATUS
from .serializers import ErrataSerializer
from .forms import ErrataModelForm
from oxauth.functions import get_user_info


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
    queryset = Errata.objects.prefetch_related("book").all()
    serializer_class = ErrataSerializer
    http_method_names = ['get', 'post', 'head']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ErrataFilter
    ordering_fields = ('id', 'resolution_date', 'created', 'modified', )


def duplicate(errata):
    errata.pk = None
    errata.save()
    return redirect('/apps/cms/api/errata/admin/edit/{}'.format(errata.pk)) #TODO: Change to use url resolver name
