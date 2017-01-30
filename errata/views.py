from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet
from .models import Errata
from .serializers import ErrataSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class ErrataView(ModelViewSet):
    serializer_class = ErrataSerializer
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        return Errata.objects.all()