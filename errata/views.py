from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from .models import Errata
from .serializers import ErrataSerializer, ErratumSerializer


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


class ErratumView(ModelViewSet):
    serializer_class = ErratumSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        return Errata.objects.all()