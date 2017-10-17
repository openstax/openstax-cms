from django.contrib import admin

from .models import Mail


class MailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'to_address']

admin.site.register(Mail, MailAdmin)
