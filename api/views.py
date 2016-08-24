from django.core.management import call_command
from django.utils.six import StringIO
from django.http import JsonResponse
from rest_framework import viewsets
from salesforce.models import Adopter
from salesforce.functions import check_if_faculty_pending
from social.apps.django_app.default.models import \
    DjangoStorage as SocialAuthStorage
from wagtail.wagtailimages.models import Image

from .serializers import AdopterSerializer, ImageSerializer


class AdopterViewSet(viewsets.ModelViewSet):
    queryset = Adopter.objects.all()
    serializer_class = AdopterSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


def user_api(request):
    user = request.user

    try:
        social_auth = SocialAuthStorage.user.get_social_auth_for_user(user)
        user.accounts_id = social_auth[0].uid
    except:
        user.accounts_id = None

    return JsonResponse({
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'groups': list(user.groups.values_list('name', flat=True)),
        'accounts_id': user.accounts_id,
    })


def user_salesforce_update(request):
    user = request.user
    salesforce_faculty_verified_failed = False
    salesforce_verification_pending_failed = False

    # get user account ID
    try:
        social_auth = SocialAuthStorage.user.get_social_auth_for_user(user)
        user.accounts_id = social_auth[0].uid
    except:
        user.accounts_id = None

    # check if user is faculty_verified in SF
    try:
        out = StringIO()
        call_command('update_faculty_status', str(user.pk), stdout=out)
    except:
        salesforce_faculty_verified_failed = True

    # check if there is a record in SF for this user - if so, they are pending verification
    try:
        pending_verification = check_if_faculty_pending(user.pk)
        return JsonResponse({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'groups': list(user.groups.values_list('name', flat=True)),
            'accounts_id': user.accounts_id,
            'pending_verification': pending_verification,
            'salesforce_faculty_verified_failed': salesforce_faculty_verified_failed,
            'salesforce_verification_pending_failed': salesforce_verification_pending_failed,
        })

    except:
        return JsonResponse({})
