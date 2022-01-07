from django.contrib import admin
from django.core import management
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import ThankYouNote, DonationPopup, Fundraiser


class ThankYouNoteAdmin(admin.ModelAdmin):
    list_display = ['thank_you_note', 'first_name', 'last_name', 'institution', 'created']
    list_filter = (['created', 'consent_to_share_or_contact'])
    search_fields = ['created', 'consent_to_share_or_contact']
    actions = ['export_as_csv']

    def has_add_permission(self, request):
        return False

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="thank-you-notes.csv"'

        writer = csv.writer(response)
        writer.writerow(["Id",
                         "Thank You Note",
                         "First Name",
                         "Last Name",
                         "Institution",
                         "Created Date",
                         "Consent To Share Or Contact",
                         "Contact Email Address"])
        for t in queryset:
            writer.writerow([t.pk,
                             t.thank_you_note,
                             t.first_name,
                             t.last_name,
                             t.institution,
                             t.created,
                             t.consent_to_share_or_contact,
                             t.contact_email_address])

        return response


class DonationPopupAdmin(admin.ModelAdmin):
    display_list = ('download_image',
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


class FundraiserAdmin(admin.ModelAdmin):
    display_list = ('color_scheme',
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


admin.site.register(ThankYouNote, ThankYouNoteAdmin)
admin.site.register(DonationPopup, DonationPopupAdmin)
admin.site.register(Fundraiser, FundraiserAdmin)
