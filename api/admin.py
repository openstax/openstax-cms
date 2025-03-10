from import_export import fields, resources
from import_export.admin import ExportActionModelAdmin, ExportActionMixin
from import_export.widgets import ForeignKeyWidget

from django.contrib import admin
from .models import CustomizationRequest, FeatureFlag, WebviewSettings
from books.models import Book


class CustomizationRequestResource(resources.ModelResource):
    book = fields.Field(
                column_name='book',
                attribute='book',
                widget=ForeignKeyWidget(Book, 'title'))

    class Meta:
        model = CustomizationRequest
        fields = ('id', 'email', 'created', 'complete', 'num_students', 'book', 'reason', 'modules')
        export_order = ('id', 'email', 'created', 'complete', 'num_students', 'book', 'reason', 'modules')


class CustomizationRequestAdmin(ExportActionModelAdmin):
    resource_class = CustomizationRequestResource
    actions = ['mark_completed', ExportActionMixin.export_admin_action]
    list_display = ['email', 'created', 'complete', 'num_students', 'book', "reason", "modules"]
    search_fields = ['email', ]
    list_filter = ['complete', 'book']

    def mark_completed(self, request, queryset):
        queryset.update(complete=True)
    mark_completed.short_description = "Mark requests as complete"

    def has_add_permission(self, request):
        return False


class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['name', 'feature_active']
    search_fields = ['name', ]
    list_filter = ['feature_active', ]


class WebviewSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name', ]

admin.site.register(CustomizationRequest, CustomizationRequestAdmin)
admin.site.register(FeatureFlag, FeatureFlagAdmin)
admin.site.register(WebviewSettings, WebviewSettingsAdmin)
