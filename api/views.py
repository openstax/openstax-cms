from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import ImageSerializer, UserSerializer
from wagtail.wagtailimages.models import Image
from accounts.salesforce import Salesforce
from django.contrib.auth.models import Group
from django.conf import settings

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer    
    def get_queryset(self):
        user = self.request.user
        # assuming only social auth is openstax accounts for now
        if not user.groups.filter(name="Faculty").exists() and hasattr(user, 'social_auth') and user.social_auth.exists():
            accounts_id = user.social_auth.values()[0]['uid']
            with Salesforce() as sf:
                status = sf.faculty_status(accounts_id)
            if status == u'Confirmed':
                faculty_group = Group.objects.get_by_natural_key('Faculty')
                user.groups.add(faculty_group)
                user.save()
        return User.objects.filter(pk=user.pk)


