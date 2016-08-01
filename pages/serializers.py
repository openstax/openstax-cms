from rest_framework import serializers

from pages.models import HomePage, HigherEducation, GeneralPage, ContactUs


class HomePageSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = HigherEducation
        fields = ('id',
                  'title',
                  'intro_heading',
                  'intro_description',
                  'row_0_box_1_content',
                  'row_0_box_1_image_url',
                  'get_row_0_box_1_image_alignment_display',
                  'row_0_box_1_cta',
                  'row_0_box_1_link',
                  'row_0_box_2_content',
                  'row_0_box_2_image_url',
                  'get_row_0_box_2_image_alignment_display',
                  'row_0_box_2_cta',
                  'row_0_box_2_link',
                  'row_0_box_3_content',
                  'row_0_box_3_image_url',
                  'get_row_0_box_3_image_alignment_display',
                  'row_0_box_3_cta',
                  'row_0_box_3_link',
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
                  'row_1_box_1_heading',
                  'row_1_box_1_image_url',
                  'row_1_box_1_description',
                  'row_1_box_1_cta',
                  'row_1_box_1_link',
                  'row_1_box_2_heading',
                  'row_1_box_2_image_url',
                  'row_1_box_2_description',
                  'row_1_box_2_cta',
                  'row_1_box_2_link',
                  'row_1_box_3_heading',
                  'row_1_box_3_image_url',
                  'row_1_box_3_description',
                  'row_1_box_3_cta',
                  'row_1_box_3_link',
                  'row_2_box_1_heading',
                  'row_2_box_1_description',
                  'row_2_box_1_cta',
                  'row_2_box_1_link',
                  'row_2_box_2_heading',
                  'row_2_box_2_description',
                  'row_2_box_2_cta',
                  'row_2_box_2_link',
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
