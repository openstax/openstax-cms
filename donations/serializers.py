from .models import ThankYouNote, DonationPopup
from rest_framework import serializers


class ThankYouNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThankYouNote
        fields = ('thank_you_note', 'first_name', 'last_name', 'institution', 'created')
        read_only_fields = ('thank_you_note', 'first_name', 'last_name', 'institution', 'created')


class DonationPopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationPopup
        fields = ('download_image',
                  'download_ready',
                  'header_image',
                  'header_title',
                  'header_subtitle',
                  'give_link_text',
                  'give_link',
                  'thank_you_link_text',
                  'thank_you_link',
                  'giving_optional',
                  'go_to_pdf_link_text',
                  'hide_donation_popup')
