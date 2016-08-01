from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from .models import GeneralPage
from .serializers import HomePageSerializer, HigherEducationSerializer, GeneralPageSerializer
from wagtail.wagtailcore.models import Page
from .models import HomePage, HigherEducation


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def page_detail(request, slug):
    """
    Retrieve, update or delete a pages JSON.
    """
    page_found = True

    try:
        page = HomePage.objects.get(slug=slug)
        serializer = HomePageSerializer(page)
        return JSONResponse(serializer.data)
    except HomePage.DoesNotExist:
        page_found = False

    try:
        page = HigherEducation.objects.get(slug=slug)
        serializer = HigherEducationSerializer(page)
        return JSONResponse(serializer.data)
    except HigherEducation.DoesNotExist:
        page_found = False

    try:
        page = GeneralPage.objects.get(slug=slug)
        serializer = GeneralPageSerializer(page)
        return JSONResponse(serializer.data)
    except GeneralPage.DoesNotExist:
        page_found = False

    if not page_found:
        return HttpResponse(status=404)
