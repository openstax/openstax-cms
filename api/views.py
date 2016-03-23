from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import ImageSerializer, UserSerializer, AdopterSerializer
from wagtail.wagtailimages.models import Image
from salesforce.models import Adopter
from django.utils.six import StringIO
from django.core.management import call_command


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
        # assuming only social auth is openstax accounts for now
        if user.groups.filter(name="Faculty").exists():
            pass
        elif hasattr(user, 'social_auth'):
            if user.social_auth.exists():
                accounts_id = str(user.social_auth.values()[0]['uid'])
                cms_id = str(user.pk)
                try:
                    out = StringIO()
                    call_command(
                        'update_faculty_status', cms_id, accounts_id, stdout=out)
                except:
                    pass
        return User.objects.filter(pk=user.pk)


