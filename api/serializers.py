from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer
from wagtail.wagtailimages.models import Image
from salesforce.models import Adopter
from social.apps.django_app.default.models import DjangoStorage as SocialAuthStorage

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
                  #'url',
                  )


class UserSerializer(UserDetailsSerializer):
    groups = serializers.StringRelatedField(many=True)
    accounts_id = serializers.CharField(required=True, allow_blank=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = ('username',
                  'first_name',
                  'last_name',
                  'is_staff',
                  'is_superuser',
                  'groups',
                  'accounts_id',)
        read_only_fields = ('username',
                            'first_name',
                            'last_name',
                            'is_staff',
                            'is_superuser',
                            'groups',
                            'accounts_id',)

