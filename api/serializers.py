from rest_framework import serializers
from salesforce.models import Adopter
from wagtail.wagtailimages.models import Image
from wagtail.wagtaildocs.models import Document


class AdopterSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Adopter
        fields = ('name',
                  'description',
                  'website',)


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = ('id',
                  'file',
                  'title',
                  'height',
                  'width',
                  'created_at',
                  )


class DocumentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Document
        fields = ('id',
                  'file',
                  'title',
                  'created_at',
                  )