from .models import Role, Subject, K12Subject, ErrataContent, SubjectCategory, GiveBanner, BlogContentType, \
    BlogCollection, NoWebinarMessage

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



class K12SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = K12Subject
        fields = ('id',
                  'name', 
                  'intro_text', 
                  'subject_image', 
                  'subject_category' , 
                  'subject_color', 
                  'subject_link'
                  )


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


class NoWebinarMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoWebinarMessage
        fields = ('no_webinar_message',)

