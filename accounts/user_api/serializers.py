from django.contrib.auth.models import User
from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer

class UserSerializer(UserDetailsSerializer):

    class Meta(UserDetailsSerializer.Meta):
        fields = ('first_name', 'last_name', 'email', 'is_staff', 'is_superuser')
        read_only_fields = ('first_name', 'last_name', 'email', 'is_staff', 'is_superuser')
