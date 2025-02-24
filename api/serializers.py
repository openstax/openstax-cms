from rest_framework import serializers
from salesforce.models import Adopter
from wagtail.images.models import Image
from wagtail.documents.models import Document
from api.models import CustomizationRequest


class AdopterSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Adopter
        fields = ('name',
                  'description',
                  'website',)
        read_only_fields = ('name',
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
        read_only_fields = ('id',
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
        read_only_fields = ('id',
                          'file',
                          'title',
                          'created_at',
                          )


class ModuleListingField(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class CustomizationRequestSerializer(serializers.ModelSerializer):
    modules = ModuleListingField(many=True)

    def create(self, validated_data):
        modules = list(validated_data.get("modules", None))
        validated_data.pop('modules')
        # clean the modules so they are easier to read in the admin/export
        modules = ', '.join(str(x) for x in modules)

        return CustomizationRequest.objects.create(modules=modules, **validated_data)


    class Meta:
        model = CustomizationRequest
        fields = ('email', 'num_students', 'reason', 'modules', 'book')
