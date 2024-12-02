from django.shortcuts import redirect
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .models import BookIndex, Book
from .serializers import FacultyResourcesSerializer


@csrf_exempt
def book_index(request):
    try:
        page = BookIndex.objects.all()[0]
        return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
    except IndexError:
        raise Http404("Subject page not found")


@csrf_exempt
def book_detail(request, slug):
    try:
        page = Book.objects.get(slug=slug)
        return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
    except Book.DoesNotExist:
        raise Http404("Book does not exist.")


class ResourcesViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=True)
    def list(self, request):
        slug = request.GET.get('slug', False)
        queryset = Book.objects.filter(slug=slug)
        if queryset:
            if queryset[0].book_state == 'retired':
                raise NotFound('This book is retired. The latest version can be found at https://openstax.org')

            serializer = FacultyResourcesSerializer(queryset[0], context={'request': request})
            return Response(serializer.data)
        else:
            return Response({})

