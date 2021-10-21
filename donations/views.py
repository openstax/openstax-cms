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
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        institution = request.data['institution']
        consent_to_share_or_contact = request.data['consent_to_share_or_contact']
        contact_email_address = request.data['contact_email_address']

        ty_note = ThankYouNote.objects.create(thank_you_note=thank_you_note,
                                              first_name=first_name,
                                              last_name=last_name,
                                              institution=institution,
                                              consent_to_share_or_contact=consent_to_share_or_contact,
                                              contact_email_address=contact_email_address)

        serializer = ThankYouNoteSerializer(data=request.data)
        if serializer.is_valid():
            return JsonResponse(status=201, data=serializer.data)


class DonationPopupViewSet(viewsets.ModelViewSet):
    serializer_class = DonationPopupSerializer
    queryset = DonationPopup.objects.all()
    http_method_names = ['get']