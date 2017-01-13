from .models import Errata

from rest_framework import serializers


class ErrataListSerializer(serializers.ListSerializer):



class ErrataSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    error_type = serializers.StringRelatedField()
    resource = serializers.StringRelatedField(many=True)

    class Meta:
        model = Errata
        fields = '__all__'
