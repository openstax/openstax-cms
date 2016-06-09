from rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from salesforce.models import Adopter
from wagtail.wagtailimages.models import Image


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


class UserSerializer(UserDetailsSerializer):
    groups = serializers.StringRelatedField(many=True)
    accounts_id = serializers.CharField(required=True, allow_blank=True)
    pending_verification = serializers.BooleanField()

    class Meta(UserDetailsSerializer.Meta):
        fields = ('username',
                  'first_name',
                  'last_name',
                  'is_staff',
                  'is_superuser',
                  'groups',
                  'accounts_id',
                  'pending_verification',)
        read_only_fields = ('username',
                            'first_name',
                            'last_name',
                            'is_staff',
                            'is_superuser',
                            'groups',
                            'accounts_id',
                            'pending_verification',)

