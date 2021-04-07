from import_export import resources
from import_export.admin import ExportActionModelAdmin, ExportActionMixin

from django.contrib import admin
from .models import CustomizationRequest
from wagtail.core.models import Page

class CustomizationRequestResource(resources.ModelResource):
    class Meta:
        model = CustomizationRequest
        fields = ('id', 'email', 'created', 'complete', 'num_students', 'book', 'reason', 'modules')
        export_order = ('id', 'email', 'created', 'complete', 'num_students', 'book', 'reason', 'modules')

    def dehydrate_book(self, export_item):
        page = Page.objects.get(id=export_item.book_id)
        return page.title


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

admin.site.register(CustomizationRequest, CustomizationRequestAdmin)
