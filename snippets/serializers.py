<<<<<<< HEAD
from .models import Role, Subject, ErrataContent, SubjectCategory, GiveBanner, BlogContentType, BlogCollection
=======
from .models import Role, Subject, ErrataContent, SubjectCategory, GiveBanner, ContentLicense
>>>>>>> Added Content License snippet and drop down to select license of book

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


class GiveBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveBanner
        fields = ('html_message',
                  'link_text',
                  'link_url',
                  'banner_thumbnail')


class BlogContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContentType
        fields = ('content_type',)


class BlogCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCollection
        fields = ('name',
                  'description',
                  'collection_image')


class ContentLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLicense
        fields = ('license_code',
                  'version',
                  'license_name',
                  'license_url')
