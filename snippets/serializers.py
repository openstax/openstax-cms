from .models import Role

from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Role
        fields = ('id',
                  'name')
