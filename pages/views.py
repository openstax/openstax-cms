import json

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PardotFormPage


@api_view(['POST'])
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

    # Validate that submitted fields match defined form fields
    defined_fields = {f.clean_name for f in page.get_form_fields()}
    submitted_data = request.data

    if not submitted_data:
        return Response(
            {'error': 'No form data submitted.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check required fields
    for field in page.get_form_fields():
        if field.required and not submitted_data.get(field.clean_name):
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
