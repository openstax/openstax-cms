from rest_framework import viewsets
from .models import Menus
from .serializers import MenusSerializer


class MenusViewSet(viewsets.ModelViewSet):
    queryset = Menus.objects.all()
    serializer_class = MenusSerializer