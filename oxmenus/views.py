from rest_framework import viewsets
from .models import Menus
from .serializers import OXMenusSerializer


class OXMenusViewSet(viewsets.ModelViewSet):
    queryset = Menus.objects.all()
    serializer_class = OXMenusSerializer
