from .models import Errata

from rest_framework import serializers


class ErrataSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    error_type = serializers.StringRelatedField()
    resource = serializers.StringRelatedField(many=True)

    class Meta:
        model = Errata
        fields = '__all__'


class ErrataListSerializer(serializers.ListSerializer):
    child = ErrataSerializer()
