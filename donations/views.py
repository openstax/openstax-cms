from rest_framework import viewsets
from .models import ThankYouNote, DonationPopup
from .serializers import ThankYouNoteSerializer, DonationPopupSerializer
from rest_framework.decorators import action
from django.utils import timezone
from django.http import JsonResponse


class ThankYouNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ThankYouNoteSerializer

    @action(methods=['post'], detail=True)
    def post(self, request):
        thank_you_note = request.data['thank_you_note']
        user_info = request.data['user_info']
        created = timezone.now()
        try:
            ty_note = ThankYouNote(thank_you_note=thank_you_note, user_info=user_info, created=created)
            ty_note.save()
        except:
            ty_note = ThankYouNote.objects.create(thank_you_note=thank_you_note, user_info=user_info, created=created)

        serializer = ThankYouNoteSerializer(data=request.data)
        if serializer.is_valid():
            return JsonResponse(status=201, data=serializer.data)


class DonationPopupViewSet(viewsets.ModelViewSet):
    serializer_class = DonationPopupSerializer
    queryset = DonationPopup.objects.all()
    http_method_names = ['get']