from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from .models import Errata
from .serializers import ErrataSerializer, ErrataListSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def errata_detail(request, id):
    try:
        errata = Errata.objects.get(pk=id)
        serializer = ErrataSerializer(errata)
        return JSONResponse(serializer.data)
    except Errata.DoesNotExist:
        return HttpResponse(status=404)


def errata_list(request):
    queryset = Errata.objects.filter()
    serializer = ErrataListSerializer(queryset)
    return JSONResponse(serializer.data)
