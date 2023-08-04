from rest_framework import serializers
from .models import Webinar


class WebinarSerializer(serializers.ModelSerializer):
    subjects = serializers.SerializerMethodField()
    collections = serializers.SerializerMethodField()

    def get_subjects(self, obj):
        return obj.selected_subjects_json()

    def get_collections(self, obj):
        return obj.selected_collections_json()

    class Meta:
        model = Webinar
        fields = ('id',
                  'start',
                  'end',
                  'title',
                  'description',
                  'speakers',
                  'spaces_remaining',
                  'registration_url',
                  'registration_link_text',
                  'display_on_tutor_page',
                  'subjects',
                  'collections')
        read_only_fields = ('id',
                            'start',
                            'end',
                            'title',
                            'description',
                            'speakers',
                            'spaces_remaining',
                            'registration_url',
                            'registration_link_text',
                            'display_on_tutor_page',
                            'subjects',
                            'collections')
