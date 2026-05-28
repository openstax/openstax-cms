from rest_framework import viewsets
from .models import ThankYouNote, DonationPopup, Fundraiser, SiteBanner
from .serializers import ThankYouNoteSerializer, DonationPopupSerializer, FundraiserSerializer, SiteBannerSerializer
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse


class ThankYouNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ThankYouNoteSerializer

    @action(methods=['post'], detail=True)
    def post(self, request):
        thank_you_note = request.data['thank_you_note']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        institution = request.data['school']
        consent_to_share_or_contact = request.data.get('consent_to_share_or_contact', False)
        contact_email_address = request.data.get('contact_email_address', '')
        source = request.data.get('source', '')

        ty_note = ThankYouNote.objects.create(thank_you_note=thank_you_note,
                                              first_name=first_name,
                                              last_name=last_name,
                                              institution=institution,
                                              consent_to_share_or_contact=consent_to_share_or_contact,
                                              contact_email_address=contact_email_address,
                                              source=source)

        serializer = ThankYouNoteSerializer(data=request.data)
        if serializer.is_valid():
            return JsonResponse(status=201, data=serializer.data)


class DonationPopupViewSet(viewsets.ModelViewSet):
    serializer_class = DonationPopupSerializer
    queryset = DonationPopup.objects.all()
    http_method_names = ['get']


class FundraiserViewSet(viewsets.ModelViewSet):
    serializer_class = FundraiserSerializer
    queryset = Fundraiser.objects.all()
    http_method_names = ['get']


class SiteBannerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SiteBannerSerializer

    def get_queryset(self):
        now = timezone.now()
        return SiteBanner.objects.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )