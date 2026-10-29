import os

from rest_framework import viewsets
from .models import ThankYouNote, DonationPopup, DonationLink, Fundraiser, SiteBanner
from .serializers import (ThankYouNoteSerializer, DonationPopupSerializer, DonationLinkSerializer,
                           FundraiserSerializer, SiteBannerSerializer)
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

# The thank-you note form lets people attach a photo or video. Extensions rather
# than content types: the browser supplies the type (HEIC often arrives as
# application/octet-stream), and the file is served from the media domain by its
# extension. SVG is left out on purpose, since it can carry script.
ATTACHMENT_EXTENSIONS = frozenset({
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif',
    '.mp4', '.mov', '.m4v', '.webm',
})
ATTACHMENT_MAX_BYTES = 100 * 1024 * 1024


def attachment_error(upload):
    """ Why `upload` can't be stored, or None if it can. """
    extension = os.path.splitext(upload.name)[1].lower()
    if extension not in ATTACHMENT_EXTENSIONS:
        return 'Attach a photo or a video (JPG, PNG, GIF, WEBP, HEIC, MP4, MOV, M4V or WEBM).'
    if upload.size > ATTACHMENT_MAX_BYTES:
        return 'The file is too large. The limit is {} MB.'.format(
            ATTACHMENT_MAX_BYTES // (1024 * 1024))
    return None


class ThankYouNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ThankYouNoteSerializer

    @action(methods=['post'], detail=True)
    def post(self, request):
        thank_you_note = str(request.data.get('thank_you_note') or '').strip()
        if not thank_you_note:
            return JsonResponse(status=400, data={'thank_you_note': 'This field is required.'})

        # Checked before anything is saved, so a rejected file doesn't leave a
        # note behind with the attachment missing.
        attachment = request.FILES.get('attachment')
        if attachment:
            error = attachment_error(attachment)
            if error:
                return JsonResponse(status=400, data={'attachment': error})

        # 'institution' is the pre-2025 field name, still posted by stale cached SPA bundles
        institution = request.data.get('school') or request.data.get('institution', '')

        ty_note = ThankYouNote.objects.create(thank_you_note=thank_you_note,
                                              first_name=request.data.get('first_name', ''),
                                              last_name=request.data.get('last_name', ''),
                                              institution=institution,
                                              consent_to_share_or_contact=request.data.get('consent_to_share_or_contact', False),
                                              contact_email_address=request.data.get('contact_email_address', ''),
                                              source=request.data.get('source', ''),
                                              account_uuid=request.data.get('account_uuid') or None,
                                              attachment=attachment)

        return JsonResponse(status=201, data=ThankYouNoteSerializer(ty_note).data)


class DonationPopupViewSet(viewsets.ModelViewSet):
    serializer_class = DonationPopupSerializer
    queryset = DonationPopup.objects.all()
    http_method_names = ['get']


class DonationLinkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationLinkSerializer

    def get_queryset(self):
        return DonationLink.objects.filter(is_active=True)


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