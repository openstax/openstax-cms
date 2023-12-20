from .models import ThankYouNote, DonationPopup, Fundraiser
from rest_framework import serializers


class ThankYouNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThankYouNote
        fields = ('thank_you_note',
                  'first_name',
                  'last_name',
                  'institution',
                  'created',
                  'consent_to_share_or_contact',
                  'contact_email_address',
                  'source')
        read_only_fields = ('thank_you_note',
                            'first_name',
                            'last_name',
                            'institution',
                            'created',
                            'consent_to_share_or_contact',
                            'contact_email_address',
                            'source')


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
        read_only_fields = ('download_image',
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


class FundraiserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fundraiser
        fields = ('color_scheme',
                  'message_type',
                  'headline',
                  'message',
                  'button_text',
                  'button_url',
                  'box_headline',
                  'box_html',
                  'fundraiser_image',
                  'goal_amount',
                  'goal_time',)
        read_only_fields = ('color_scheme',
                  'message_type',
                  'headline',
                  'message',
                  'button_text',
                  'button_url',
                  'box_headline',
                  'box_html',
                  'fundraiser_image',
                  'goal_amount',
                  'goal_time',)

