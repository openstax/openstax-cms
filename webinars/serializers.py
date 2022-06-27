from rest_framework import serializers
from .models import Webinar


class WebinarSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     super(WebinarSerializer, self).__init__(*args, **kwargs)
    #
    #     for field in self.fields:
    #         self.fields[field].read_only = True
    subjects = serializers.SerializerMethodField()

    def get_subjects(self, obj):
        return obj.selected_subjects_json()

    class Meta:
        model = Webinar
        fields = ('id',
                  'start',
                  'end',
                  'description',
                  'speakers',
                  'spaces_remaining',
                  'registration_url',
                  'registration_link_text',
                  'display_on_tutor_page',
                  'subjects')
        read_only_fields = ('id',
                            'start',
                            'end',
                            'description',
                            'speakers',
                            'spaces_remaining',
                            'registration_url',
                            'registration_link_text',
                            'display_on_tutor_page',
                            'subjects')
