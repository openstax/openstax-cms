from rest_framework import viewsets
from .models import Menus
from .serializers import OXMenusSerializer


class OXMenusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Menus.objects.all().order_by('sort_order')
    serializer_class = OXMenusSerializer
