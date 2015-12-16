from django.conf.urls import include, url

from wagtail.wagtailimages.models import Image
from rest_framework import routers, serializers, viewsets
from django.views.generic.base import RedirectView


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


router = routers.DefaultRouter()
router.register(r'', ImageViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]

