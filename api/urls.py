from django.conf.urls import include, url

from wagtail.wagtailimages.models import Image
from rest_framework import routers, serializers, viewsets
from django.views.generic.base import RedirectView

from rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth.models import User

router = routers.DefaultRouter()


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ('id',
                  'file',
                  'title',
                  'height',
                  'width',
                  'created_at',
                  #'url',
                  )

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


router.register(r'v0/images', ImageViewSet)


class UserSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ('first_name', 
                  'last_name', 
                  'email', 
                  'is_staff', 
                  'is_superuser')
        read_only_fields = ('first_name', 
                            'last_name', 
                            'email', 
                            'is_staff', 
                            'is_superuser')

 
class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer    
    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.pk)

router.register(r'user', UserView, 'user')

urlpatterns = [
    url(r'^', include(router.urls)),
]

