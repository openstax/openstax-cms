from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import ImageSerializer, UserSerializer, AdopterSerializer
from wagtail.wagtailimages.models import Image
from salesforce.salesforce import Salesforce
from django.contrib.auth.models import Group
from django.conf import settings
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
        try:
            out = StringIO()
            call_command('update_faculty_status', str(user.pk), stdout=out)
        except:
            pass
        return [user]


