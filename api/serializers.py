from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer
from wagtail.wagtailimages.models import Image
from wagtail.wagtailcore.models import Page

class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('id',
                  'title',
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
        fields = ('first_name', 
                  'last_name', 
                  'email', 
                  'is_staff', 
                  'is_superuser',
                  'groups')
        read_only_fields = ('first_name', 
                            'last_name', 
                            'email', 
                            'is_staff', 
                            'is_superuser',
                            'groups')

