from django.shortcuts import redirect
from rest_framework import viewsets
from salesforce.models import Adopter
from salesforce.functions import check_if_faculty_pending
from social.apps.django_app.default.models import \
    DjangoStorage as SocialAuthStorage
from wagtail.wagtailimages.models import Image

from accounts.models import UserPendingVerification

from .serializers import AdopterSerializer, ImageSerializer, UserSerializer


class AdopterViewSet(viewsets.ModelViewSet):
    queryset = Adopter.objects.all()
    serializer_class = AdopterSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user

        try:
            social_auth = SocialAuthStorage.user.get_social_auth_for_user(user)
            user.accounts_id = social_auth[0].uid
        except:
            user.accounts_id = None

        try:
            pending_verification = UserPendingVerification.objects.get(user=user)
            if pending_verification:
                user.pending_verification = True
        except (UserPendingVerification.DoesNotExist, TypeError) as e: #TypeError catches when it's an anon user
            user.pending_verification = False

        return [user]


def check_pending(request):
    user = request.user

    # check if there is a record in salesforce for this user - if so, they are pending verification
    try:
        _ = UserPendingVerification.objects.get(user=user, pending_verification=True)
    except UserPendingVerification.DoesNotExist:
        if check_if_faculty_pending(user.pk):
            UserPendingVerification.objects.create(user=user, pending_verification=True)
        return redirect('/api/user/')


