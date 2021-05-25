from rest_framework import viewsets
from .models import ThankYouNote
from .serializers import ThankYouNoteSerializer


class ThankYouNoteViewSet(viewsets.ModelViewSet):
    queryset = ThankYouNote.objects.all()
    serializer_class = ThankYouNoteSerializer
