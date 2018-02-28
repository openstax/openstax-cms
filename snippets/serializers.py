from .models import Role, Version

from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Role
        fields = ('id',
                  'display_name',
                  'salesforce_name')


class VersionSerializer(serializers.ModelSerializer):
    version = serializers.CharField(read_only=True)

    class Meta:
        model = Version
        fields = ('version',
                  'created')
