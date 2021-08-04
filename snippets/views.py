from rest_framework import viewsets

from .models import Role, Subject, ErrataContent
from .serializers import RoleSerializer, SubjectSerializer, ErrataContentSerializer

from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend

SPANISH_LOCALE_ID = 2
ENGLISH_LOCALE_ID = 1

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class SubjectList(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = Subject.objects.all()
        name = self.request.query_params.get('name', None)
        locale = self.request.query_params.get('locale', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        if locale is not None:
            queryset = queryset.filter(locale=convert_locale(locale))
        return queryset


class ErrataContentViewSet(viewsets.ModelViewSet):
    serializer_class = ErrataContentSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = ErrataContent.objects.all()
        book_state = self.request.query_params.get('book_state', None)
        locale = self.request.query_params.get('locale', None)
        if book_state is not None:
            queryset = queryset.filter(book_state=book_state)
        if locale is not None:
            queryset = queryset.filter(locale=convert_locale(locale))
        return queryset


def convert_locale(locale):
    if locale == 'es':
        return SPANISH_LOCALE_ID
    return ENGLISH_LOCALE_ID
