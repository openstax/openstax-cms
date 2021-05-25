from .models import ThankYouNote
from rest_framework import serializers


class ThankYouNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThankYouNote
        fields = ('thank_you_note', 'user_info', 'created')
        read_only_fields = ('thank_you_note', 'user_info', 'created')
