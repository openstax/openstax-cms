from rest_framework import viewsets
from .serializers import ImageSerializer, UserSerializer, AdopterSerializer
from wagtail.wagtailimages.models import Image
from salesforce.models import Adopter
from django.utils.six import StringIO
from django.core.management import call_command
from social.apps.django_app.default.models import DjangoStorage as SocialAuthStorage

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
            out = StringIO()
            call_command('update_faculty_status', str(user.pk), stdout=out)
        except:
            pass

        return [user]


