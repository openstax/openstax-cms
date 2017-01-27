from .models import Errata

from rest_framework import serializers


class ErrataSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    error_type = serializers.StringRelatedField()
    resource = serializers.StringRelatedField(many=True)

    class Meta:
        model = Errata
        fields = '__all__'


class ErratumSerializer(serializers.ModelSerializer):
    erratum = ErrataSerializer(many=True, read_only=True)

    class Meta:
        model = Errata
        fields = '__all__'
