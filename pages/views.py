from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from .models import GeneralPage
from .serializers import GeneralPageSerializer
from wagtail.wagtailcore.models import Page


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def page_list(request):
    """
    List all code snippets, or create a new snippet.
    """

    if request.method == 'GET':
        pages = GeneralPage.objects.all()
        serializer = GeneralPageSerializer(pages, many=True)
        return JSONResponse(serializer.data)


@csrf_exempt
def page_detail(request, slug):
    """
    Retrieve, update or delete a pages JSON.
    """
    try:
        page = GeneralPage.objects.get(slug=slug)
        serializer = GeneralPageSerializer(page)
        return JSONResponse(serializer.data)
    except Page.DoesNotExist:
        return HttpResponse(status=404)
