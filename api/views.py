from rest_framework import viewsets
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
        try:
            out = StringIO()
            call_command('update_faculty_status', str(user.pk), stdout=out)
        except:
            pass
        return [user]


