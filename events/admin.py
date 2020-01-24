from import_export import resources
from import_export.admin import ExportActionModelAdmin

from inline_actions.admin import InlineActionsModelAdminMixin

from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .models import Event, Session, Registration

class SessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'seats_remaining']
    list_filter = ('location', 'date')
    search_fields = ['name', ]


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration
        fields = ('first_name', 'last_name', 'registration_email', 'session__name', 'checked_in')

class RegistrationAdmin(InlineActionsModelAdminMixin, ExportActionModelAdmin):
    list_display = ('full_name', 'registration_email', 'checked_in')
    search_fields = ('last_name', 'registration_email')
    list_filter = ['session', ]
    resource_class = RegistrationResource

    inline_actions = ['toggle_check_in',]

    def toggle_check_in(self, request, obj, parent_obj=None):
        if not obj.checked_in:
            obj.checked_in = timezone.now()
        else:
            obj.checked_in = None
        obj.save()

        if obj.checked_in:
            messages.success(request, _("User marked as checked in."))
        else:
            messages.warning(request, _("User marked as not checked in."))

    def get_toggle_check_in_label(self, obj):
        if not obj.checked_in:
            return 'Check In'
        return 'Uncheck In'

    class Media:
        js = ('js/custom_admin.js', )


admin.site.register(Event)
admin.site.register(Session, SessionAdmin)
admin.site.register(Registration, RegistrationAdmin)
