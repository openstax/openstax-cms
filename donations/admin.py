from django.contrib import admin
from django.core import management
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import ThankYouNote


class ThankYouNoteAdmin(admin.ModelAdmin):
    list_display = ['thank_you_note', 'user_info', 'created']
    list_filter = ('created',)
    search_fields = ['user_info', 'created']
    actions = ['export_as_csv']

    def has_add_permission(self, request):
        return False

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="thank-you-notes.csv"'

        writer = csv.writer(response)
        writer.writerow(["Id",
                         "Thank You Note",
                         "User Info",
                         "Created Date"])
        for t in queryset:
            writer.writerow([t.pk,
                             t.thank_you_note,
                             t.user_info,
                             t.created])

        return response


admin.site.register(ThankYouNote, ThankYouNoteAdmin)
