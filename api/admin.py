from import_export import resources
from import_export.admin import ExportActionModelAdmin, ExportActionMixin
from import_export.formats import base_formats

from django.contrib import admin
from .models import CustomizationRequest

class CustomizationRequestResource(resources.ModelResource):
    class Meta:
        model = CustomizationRequest
        fields = ('id', 'email', 'complete', 'num_students', 'reason', 'modules')
        export_order = ('id', 'email', 'complete', 'num_students', 'reason', 'modules')


class CustomizationRequestAdmin(ExportActionModelAdmin):
    resource_class = CustomizationRequestResource
    actions = ['mark_completed', ExportActionMixin.export_admin_action]
    list_display = ['email', 'complete', 'num_students', "reason", "modules"]
    search_fields = ['email', ]
    list_filter = ['complete']

    def mark_completed(self, request, queryset):
        queryset.update(complete=True)
    mark_completed.short_description = "Mark requests as complete"

    def has_add_permission(self, request):
        return False

admin.site.register(CustomizationRequest, CustomizationRequestAdmin)
