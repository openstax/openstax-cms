from statistics import mean

import django_filters
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, MultipleChoiceFilter
from django.shortcuts import render, redirect
from .models import (Errata, ERRATA_STATUS, NEW, EDITORIAL_REVIEW, K12_EDITORIAL_REVIEW,
                      CARTRIDGE_REVIEW, OPENSTAX_EDITORIAL_REVIEW)
from .serializers import ErrataSerializer
from wagtail.admin.viewsets.model import ModelViewSet as WagtailModelViewSet

OPEN_STATUSES = (NEW, EDITORIAL_REVIEW, K12_EDITORIAL_REVIEW, CARTRIDGE_REVIEW, OPENSTAX_EDITORIAL_REVIEW)


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
    add_to_admin_menu = False
    exclude_form_fields = []

errata_viewset = ErrataModelViewSet("errata")

def duplicate(errata):
    errata.pk = None
    errata.save()
    return redirect('/apps/cms/api/errata/admin/edit/{}'.format(errata.pk)) #TODO: Change to use url resolver name


def errata_dashboard(request):
    if not request.user.has_perm('errata.view_errata'):
        raise PermissionDenied

    status_counts = dict(Errata.objects.values_list('status').annotate(count=Count('id')))
    funnel = [{'label': label, 'count': status_counts.get(value, 0)} for value, label in ERRATA_STATUS]
    max_funnel_count = max((row['count'] for row in funnel), default=0)
    for row in funnel:
        row['pct'] = round(100 * row['count'] / max_funnel_count) if max_funnel_count else 0

    resolved = Errata.objects.filter(resolution_date__isnull=False).values_list('created', 'resolution_date')
    resolution_days = [(resolution_date - created.date()).days for created, resolution_date in resolved]
    avg_resolution_days = round(mean(resolution_days), 1) if resolution_days else None

    oldest_open = list(
        Errata.objects.filter(status__in=OPEN_STATUSES, archived=False, junk=False)
        .select_related('book').order_by('created')[:10]
    )

    per_book = list(
        Errata.objects.filter(archived=False, junk=False)
        .values('book__title').annotate(count=Count('id')).order_by('-count')[:15]
    )
    max_book_count = per_book[0]['count'] if per_book else 0
    for row in per_book:
        row['pct'] = round(100 * row['count'] / max_book_count) if max_book_count else 0

    context = admin.site.each_context(request)
    context.update({
        'title': 'Errata Dashboard',
        'funnel': funnel,
        'avg_resolution_days': avg_resolution_days,
        'resolved_count': len(resolution_days),
        'oldest_open': oldest_open,
        'per_book': per_book,
    })
    return render(request, 'errata_dashboard.html', context)
