from random import randrange
from urllib.parse import urlparse

from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from openstax.functions import remove_locked_links_detail
from .models import BookIndex, Book, FacultyResources
from .serializers import FacultyResourcesSerializer


@csrf_exempt
def book_index(request):
    page = BookIndex.objects.all()[0]
    return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))


@csrf_exempt
def book_detail(request, slug):
    x_param = request.GET.get('x', False)
    print(str(request))
    print('x_param: ' + str(x_param))
    # print('request.path: ' + str(request.path))
    # if '?' in request.path:
    #     query = urlparse(request.path).query
    #     print('query:' + str(query))
    try:
        page = Book.objects.get(slug=slug)
        if x_param == 'y':
            return redirect('/apps/cms/api/v2/pages/{}/?x=y'.format(page.pk))
        else:
            return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
    except Book.DoesNotExist:
        raise Http404("Book does not exist.")

# @csrf_exempt
# def resources(request):
#     x_param = request.GET.get('x', False)
#     slug = request.GET.get('slug', False)
#     try:
#         queryset = Book.objects.get(slug=slug)
#         faculty_resources = []
#         video_resources = []
#         orientation_resources = []
#         for faculty_resource in queryset.book_faculty_resources.values():
#             print(FacultyResources.objects.filter(id=faculty_resource['link_document_id']).values())
#             faculty_resources.append(faculty_resource)
#
#         faculty_resource_json = {}
#         faculty_resource_json['book_faculty_resources'] = faculty_resources
#         faculty_resource_json['book_video_faculty_resources'] = video_resources
#         faculty_resource_json['book_orientation_faculty_resources'] = orientation_resources
#         #print(str(queryset.book_faculty_resources))
#         return JsonResponse(faculty_resource_json)
#
#     except Book.DoesNotExist:
#         raise Http404("Book does not exist.")


class ResourcesViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=True)
    def list(self, request):
        slug = request.GET.get('slug', False)
        queryset = Book.objects.filter(slug=slug)
        print('queryset: ' + str(queryset[0]))
        serializer = FacultyResourcesSerializer(queryset[0], context={'request': request})
        #print('serializer.data: ' + str(serializer.data.values()))
        return Response(serializer.data)

