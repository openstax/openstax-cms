from rest_framework import serializers
from rest_framework.fields import Field

from pages.models import HomePage, HigherEducation, GeneralPage, ContactUs


class StreamField(Field):
    """
    This is copying how Wagtail handles StreamFields, otherwise the JSON is output as strings instead of dicts.
    """
    def to_representation(self, value):
        return value.stream_block.get_prep_value(value)


class HomePageSerializer(serializers.ModelSerializer):
    row_1 = StreamField()
    row_2 = StreamField()
    row_3 = StreamField()
    row_4 = StreamField()
    row_5 = StreamField()
    
    class Meta:
        model = HomePage
        fields = ('id',
                  'title',
                  'row_1',
                  'row_2',
                  'row_3',
                  'row_4',
                  'row_5',
                  'slug',
                  'seo_title',
                  'search_description',
                  )


class HigherEducationSerializer(serializers.ModelSerializer):
    row_1 = StreamField()
    row_2 = StreamField()
    row_3 = StreamField()

    class Meta:
        model = HigherEducation
        fields = ('id',
                  'title',
                  'intro_heading',
                  'intro_description',
                  'row_1',
                  'get_started_heading',
                  'get_started_step_1_heading',
                  'get_started_step_1_description',
                  'get_started_step_1_cta',
                  'get_started_step_2_heading',
                  'get_started_step_2_description',
                  'get_started_step_2_cta',
                  'get_started_step_3_heading',
                  'get_started_step_3_description',
                  'get_started_step_3_cta',
                  'adopt_heading',
                  'adopt_description',
                  'adopt_cta',
                  'row_2',
                  'row_3',
                  'slug',
                  'seo_title',
                  'search_description',
                  )


class GeneralPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralPage
        fields = ('id',
                  'title',
                  'body',
                  'slug',
                  'seo_title',
                  'search_description',
                  )


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ('id',
                  'title',
                  'tagline',
                  'mailing_header',
                  'mailing_address',
                  'phone_number',
                  'slug',
                  'seo_title',
                  'search_description',
                  )
