import json

from django.utils import timezone
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import PardotFormPage


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
@throttle_classes([AnonRateThrottle])
def pardot_form_submit(request, page_id):
    """
    Accepts form submissions for a PardotFormPage and stores them
    in Wagtail's FormSubmission table for backup/audit.
    """
    try:
        page = PardotFormPage.objects.get(pk=page_id)
    except PardotFormPage.DoesNotExist:
        return Response(
            {'error': 'Form page not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Only allow submissions to live/public pages
    if hasattr(page, "live") and not page.live:
        return Response(
            {'error': 'Form page not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Optional shared-secret/token check to mitigate abuse
    token_setting = getattr(settings, 'PARDOT_FORM_SUBMIT_TOKEN', None)
    if token_setting:
        request_token = request.headers.get('X-Form-Token') or request.META.get('HTTP_X_FORM_TOKEN')
        if request_token != token_setting:
            return Response(
                {'error': 'Unauthorized form submission.'},
                status=status.HTTP_403_FORBIDDEN,
            )

    # Collect the set of defined form fields for filtering submitted data
    defined_fields = {f.clean_name for f in page.get_form_fields()}
    submitted_data = request.data

    if not submitted_data:
        return Response(
            {'error': 'No form data submitted.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check required fields
    for field in page.get_form_fields():
        if field.required:
            field_name = field.clean_name
            if field_name not in submitted_data:
                return Response(
                    {'error': f'Missing required field: {field.label}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            value = submitted_data.get(field_name)
            if value is None or value == "":
                return Response(
                    {'error': f'Missing required field: {field.label}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    # Filter to only defined fields
    clean_data = {
        key: value
        for key, value in submitted_data.items()
        if key in defined_fields
    }

    # Save submission
    submission_class = page.get_submission_class()
    submission_class.objects.create(
        form_data=json.dumps(clean_data),
        page=page,
    )

    return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
