from .models import Role, Subject, ErrataContent, SubjectCategory

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
                  'search_description',
                  'subject_icon',
                  'subject_color')


class ErrataContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrataContent
        fields = ('heading',
                  'book_state',
                  'content')


class SubjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = ('subject_name',
                  'subject_category',
                  'description')
