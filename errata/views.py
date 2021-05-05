import django_filters
from django.http import HttpResponse
from django.db import models
from django.contrib.auth.decorators import permission_required
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django.shortcuts import render, redirect
from .models import Errata
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
    status__not = django_filters.CharFilter(field_name='status', exclude=True)

    class Meta:
        model = Errata
        fields = ['book_title', 'book_id', 'archived', 'is_assessment_errata', 'is_assessment_errata__not', 'status__not']


class ErrataView(ModelViewSet):
    queryset = Errata.objects.all()
    serializer_class = ErrataSerializer
    http_method_names = ['get', 'post', 'head']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ErrataFilter
    ordering_fields = ('id', 'resolution_date', 'created', 'modified', )


@permission_required('errata..erratum.can_change_errata', login_url="/admin/login/?next=/errata/dashboard/")
def dashboard(request):
    errata = Errata.objects.all()
    recent_errata = Errata.objects.filter(status='New').order_by('-created')[:10]

    new_errata_count = Errata.objects.filter(status='New').count()
    editorial_review_count = Errata.objects.filter(status='Editorial Review').count()
    reviewed_count = Errata.objects.filter(status='Reviewed').count()
    completed_count = Errata.objects.filter(status='Completed').count()

    by_book = Errata.objects.all().values("book__title").annotate(reports=models.Count("pk"))
    by_type = Errata.objects.all().values("error_type").annotate(reports=models.Count("pk"))

    for book in by_book:
        book['percent'] = round(book['reports'] * 100.0 / errata.count(), 2)


    return render(request, 'errata/dashboard.html', context={'errata': errata,
                                                             'recent_errata': recent_errata,
                                                             'new_errata_count': new_errata_count,
                                                             'editorial_review_count': editorial_review_count,
                                                             'reviewed_count': reviewed_count,
                                                             'completed_count': completed_count,
                                                             'by_book': by_book,
                                                             'by_type': by_type })


@permission_required('errata..erratum.can_change_errata', login_url="/admin/login/?next=/errata/list/")
def list(request):
    errata = Errata.objects.all().order_by('created')
    status = request.GET.get('status', False)
    book = request.GET.get('book', False)
    type = request.GET.get('type', False)
    filter = request.GET.get('filter', False)
    if status:
        errata = errata.filter(status=status)
    if book:
        errata = errata.filter(book__title=book)
    if type:
        errata = errata.filter(error_type=type)
    if filter:
        if filter == 'aec':
            errata = errata.exclude(status='Completed')

    return render(request, 'errata/list.html', {'errata': errata,
                                                'status': status,
                                                'book': book,
                                                'type': type})


@permission_required('errata..erratum.can_change_errata', login_url="/admin/login/?next=/errata/edit/")
def edit(request):
    edit_errata = request.GET.get('errata', False)
    errata = False
    user = None

    if request.method == 'POST':
        form = ErrataModelForm(request.POST, request.FILES)

        if form.is_valid():
            errata = form.save()
            if request.POST.get('duplicate', False):
                duplicate(errata)
            else:
                return redirect('/apps/cms/api/errata/admin/dashboard/') #TODO: change to URL resolver name

    else:
        if edit_errata:
            errata = Errata.objects.get(pk=edit_errata)
            user = get_user_info(errata.submitted_by_account_id)
            form = ErrataModelForm(instance=errata)
        else:
            form = ErrataModelForm()

    return render(request, 'errata/edit.html', {'errata': errata,
                                                'form': form,
                                                'user': user})


def duplicate(errata):
    errata.pk = None
    errata.save()
    return redirect('/apps/cms/api/errata/admin/edit/{}'.format(errata.pk)) #TODO: Change to use url resolver name