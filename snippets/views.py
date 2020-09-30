from rest_framework import viewsets

from .models import Role, Subject
from .serializers import RoleSerializer, SubjectSerializer

from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class SubjectList(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = Subject.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset
