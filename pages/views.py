from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from .models import (GeneralPage,
                     HomePage,
                     HigherEducation,
                     AboutUs,
                     EcosystemAllies,
                     ContactUs,
                     FoundationSupport)
from .serializers import (HomePageSerializer,
                          HigherEducationSerializer,
                          GeneralPageSerializer,
                          AboutUsSerializer,
                          EcosystemAlliesSerializer,
                          ContactUsSerializer,
                          FoundationSupportSerializer)


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
    Retrieve a pages JSON by slug.
    """
    page_found = True

    try:
        page = HomePage.objects.get(slug=slug)
        for column in page.row_1:
            for name, block in column.value.bound_blocks.items():
                if name == 'image':
                    print(block.value)
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

    try:
        page = AboutUs.objects.get(slug=slug)
        serializer = AboutUsSerializer(page)
        return JSONResponse(serializer.data)
    except AboutUs.DoesNotExist:
        page_found = False

    try:
        page = EcosystemAllies.objects.get(slug=slug)
        serializer = EcosystemAlliesSerializer(page)
        return JSONResponse(serializer.data)
    except EcosystemAllies.DoesNotExist:
        page_found = False

    try:
        page = ContactUs.objects.get(slug=slug)
        serializer = ContactUsSerializer(page)
        return JSONResponse(serializer.data)
    except ContactUs.DoesNotExist:
        page_found = False

    try:
        page = FoundationSupport.objects.get(slug=slug)
        serializer = FoundationSupportSerializer(page)
        return JSONResponse(serializer.data)
    except FoundationSupport.DoesNotExist:
        page_found = False

    if not page_found:
        return HttpResponse(status=404)
