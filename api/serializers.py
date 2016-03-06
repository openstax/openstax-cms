from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer
from wagtail.wagtailimages.models import Image
from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.models import Document


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = ('id',
                  'title',
                  'file',
                  )
class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('id',
                  'title',
                  'url',
                  )

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


class UserSerializer(UserDetailsSerializer):
    groups = serializers.StringRelatedField(many=True)
    
    class Meta(UserDetailsSerializer.Meta):
        fields = ('username',
                  'first_name',
                  'last_name',
                  'is_staff', 
                  'is_superuser',
                  'groups')
        read_only_fields = ('username',
                            'first_name',
                            'last_name', 
                            'is_staff', 
                            'is_superuser',
                            'groups')

