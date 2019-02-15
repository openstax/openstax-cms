from rest_framework import serializers
from salesforce.models import Adopter
from wagtail.images.models import Image
from wagtail.documents.models import Document
from api.models import ProgressTracker

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


class ProgressSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        progress, created = ProgressTracker.objects.update_or_create(
            account_id=validated_data.get('account_id', None),
            defaults={'progress':validated_data.get('progress', None)})
        print(created)

        return progress

    class Meta:
        model = ProgressTracker
        fields = ('account_id',
                  'progress',
                  )
