from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from .models import BookIndex, Book
from .serializers import BookIndexSerializer, BookSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def book_index(request):
    page = BookIndex.objects.all()[0]
    serializer = BookIndexSerializer(page)
    return JSONResponse(serializer.data)


@csrf_exempt
def book_detail(request, slug):
    """
    Retrieve a pages JSON by slug.
    """

    try:
        page = Book.objects.get(slug=slug)
        serializer = BookSerializer(page)
        if not request.user.groups.filter(name='Faculty').exists():
            for resource in serializer.data['book_faculty_resources']:
                try:
                    resource['link_document_url'] = None
                except KeyError:
                    pass
        return JSONResponse(serializer.data)
    except Book.DoesNotExist:
        return HttpResponse(status=404)

