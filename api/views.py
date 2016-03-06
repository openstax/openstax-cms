from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import ImageSerializer, UserSerializer, PageSerializer, DocumentSerializer  
from wagtail.wagtailimages.models import Image
from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.models import Document

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer    
    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.pk)


