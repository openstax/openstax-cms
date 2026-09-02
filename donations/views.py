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
        thank_you_note = str(request.data.get('thank_you_note') or '').strip()
        if not thank_you_note:
            return JsonResponse(status=400, data={'thank_you_note': 'This field is required.'})

        # 'institution' is the pre-2025 field name, still posted by stale cached SPA bundles
        institution = request.data.get('school') or request.data.get('institution', '')

        ty_note = ThankYouNote.objects.create(thank_you_note=thank_you_note,
                                              first_name=request.data.get('first_name', ''),
                                              last_name=request.data.get('last_name', ''),
                                              institution=institution,
                                              consent_to_share_or_contact=request.data.get('consent_to_share_or_contact', False),
                                              contact_email_address=request.data.get('contact_email_address', ''),
                                              source=request.data.get('source', ''),
                                              account_uuid=request.data.get('account_uuid') or None)

        return JsonResponse(status=201, data=ThankYouNoteSerializer(ty_note).data)


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