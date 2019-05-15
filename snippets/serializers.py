from .models import Role, Subject

from rest_framework import serializers, generics


class RoleSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Role
        fields = ('id',
                  'display_name',
                  'salesforce_name')


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id',
                  'name',
                  'page_content',
                  'seo_title',
                  'search_description')
