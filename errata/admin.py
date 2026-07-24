import unicodecsv
from import_export import resources
from import_export.admin import ExportActionMixin, ImportExportActionModelAdmin
from import_export.formats import base_formats
from import_export.fields import Field

from django.contrib import admin
from django.contrib.admin.filters import RelatedFieldListFilter
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.http import HttpResponse
from django.utils.html import mark_safe

from rangefilter.filters import DateRangeFilter

from books.constants import RETIRED
from books.models import Book
from reversion.admin import VersionAdmin

from .models import Errata, BlockedUser, EmailText, InternalDocumentation
from .forms import ErrataForm


class ErrataResource(resources.ModelResource):
    class Meta:
        model = Errata
        fields = ('id', 'created', 'modified', 'book__title', 'number_of_errors', 'is_assessment_errata', 'assessment_id', 'status', 'resolution', 'archived', 'junk', 'location', 'additional_location_information', 'detail', 'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'resource', 'file_1', 'file_2',)
        export_order = ('id', 'created', 'modified', 'book__title', 'number_of_errors', 'is_assessment_errata', 'assessment_id', 'status', 'resolution', 'archived', 'junk', 'location', 'additional_location_information', 'detail', 'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'resource',)
        
# custom export for release note generation
class CustomExportResource(resources.ModelResource):
    location = Field(attribute='location', column_name='Location')
    detail = Field(attribute='detail', column_name='Detail')
    resolution_notes = Field(attribute='resolution_notes', column_name='Resolution Notes')
    error_type = Field(attribute='error_type', column_name='Error Type')

    class Meta:
        model = Errata
        fields = ('location', 'detail', 'resolution_notes', 'error_type')
        export_order = ('location', 'detail', 'resolution_notes', 'error_type')

def custom_export_action(modeladmin, request, queryset):
    resource = CustomExportResource()
    dataset = resource.export(queryset)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Release Notes.csv"'
    response.write(dataset.csv)
    return response
custom_export_action.short_description = 'Export Errata Release Notes CSV'

class InlineInternalImage(admin.TabularInline):
    model = InternalDocumentation

class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'fullname', 'reason',)


class ActiveBookListFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        return [
            (book.pk, str(book))
            for book in Book.objects.exclude(book_state=RETIRED).order_by("title")
        ]


class ErrataAdmin(ImportExportActionModelAdmin, VersionAdmin):
    def get_queryset(self, request):
        return super(ErrataAdmin, self).get_queryset(request).select_related('book')

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',  # jquery
            'errata/errata-admin-ui.js',  # custom errata javascript
        )
    resource_class = ErrataResource
    # ordering = ['created']

    form = ErrataForm
    list_max_show_all = 10000
    list_per_page = 200
    list_display_links = ['book_title']

    search_fields = ('id',
                     'book__title',
                     'detail',
                     'location',
                     'additional_location_information',
                     )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    actions = ['mark_in_review', 'mark_OpenStax_editorial_review', 'mark_cartridge_review', 'mark_reviewed', 'mark_archived', 'mark_completed', ExportActionMixin.export_admin_action, custom_export_action]
    inlines = [InlineInternalImage, ]
    raw_id_fields = ('duplicate_id', )

    def get_export_formats(self):
        return [base_formats.CSV]

    """Actions for the Django Admin list view"""
    def mark_in_review(self, request, queryset):
        queryset.update(status='Editorial Review')
    mark_in_review.short_description = "Mark errata as Editorial Review"

    def mark_OpenStax_editorial_review(self, request, queryset):
        queryset.update(status='OpenStax Editorial Review')
    mark_OpenStax_editorial_review.short_description = "Mark errata as OpenStax Editorial Review"

    def mark_cartridge_review(self, request, queryset):
        queryset.update(status='Cartridge Review')
    mark_cartridge_review.short_description = "Mark errata as cartridge review"

    def mark_reviewed(self, request, queryset):
        queryset.update(status='Reviewed')
    mark_reviewed.short_description = "Mark errata as reviewed"

    def mark_archived(self, request, queryset):
        queryset.update(archived=True)
    mark_archived.short_description = "Mark errata as archived"

    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')
    mark_completed.short_description = "Mark errata as completed"

    def get_actions(self, request):
        actions = super(ErrataAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']

        if not request.user.groups.filter(name__in=['Content Managers']).exists():
            if 'mark_in_review' in actions:
                del actions['mark_in_review']
            if 'mark_reviewed' in actions:
                del actions['mark_reviewed']
            if 'mark_archived' in actions:
                del actions['mark_archived']
            if 'mark_completed' in actions:
                del actions['mark_completed']
        return actions

    def change_view(self, request, object_id, extra_context=None):
        if not request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers']).exists():
            extra_context = extra_context or {}
            extra_context['readonly'] = True
        return super(ErrataAdmin, self).change_view(request, object_id, extra_context=extra_context)
    
    # To enable sorting by book title on the admin page, computing field using a method
    def book_title(self, obj):
        return mark_safe(obj.book.title)
    
    book_title.admin_order_field = 'book__title'

    """Model permissions"""
    # ErrataAdmin is a single instance shared across all requests, so per-request
    # field/permission lists must be computed and returned (get_list_display,
    # get_fields, etc.) rather than assigned to self - mutating self.* here raced
    # across concurrent requests from different user roles and produced
    # "Unknown field(s) specified for Errata" 500s (Sentry OPENSTAX-CMS-VJ/VH).
    def _is_content_manager(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers']).exists()

    def _is_editorial_vendor(self, request):
        return request.user.groups.filter(name__in=['Editorial Vendor']).exists()

    def get_list_display(self, request):
        if self._is_content_manager(request):
            return ['id', 'book_title', 'created', 'modified', 'short_detail', 'number_of_errors', 'status', 'error_type', 'resource', 'location', 'additional_location_information', 'resolution', 'archived', 'junk']
        return ['id', 'book_title', 'created', 'short_detail', 'status', 'error_type', 'resource', 'location', 'created', 'archived']

    def get_list_filter(self, request):
        if self._is_content_manager(request):
            return (('created', DateRangeFilter), ('modified', DateRangeFilter), ('book', ActiveBookListFilter), 'status', 'created', 'modified', 'is_assessment_errata', 'modified', 'error_type', 'resolution', 'archived', 'junk', 'resource')
        return (('created', DateRangeFilter), ('modified', DateRangeFilter), ('book', ActiveBookListFilter), 'status', 'created', 'modified', 'is_assessment_errata', 'error_type', 'resolution', 'archived', 'resource')

    def get_fields(self, request, obj=None):
        if self._is_content_manager(request):
            return ['id', 'created', 'modified', 'book', 'is_assessment_errata', 'assessment_id', 'status',
                    'resolution', 'duplicate_id', 'location', 'additional_location_information', 'detail',
                    'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'number_of_errors',
                    'resource', 'accounts_link', 'file_1', 'file_2', 'archived', 'junk']
        elif self._is_editorial_vendor(request):
            return ['id', 'created', 'modified', 'book', 'is_assessment_errata', 'assessment_id', 'status',
                    'resolution', 'duplicate_id', 'location', 'additional_location_information', 'detail',
                    'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'number_of_errors',
                    'resource', 'accounts_user_faculty_status', 'file_1', 'file_2', 'archived']
        return ['id', 'created', 'modified', 'book', 'is_assessment_errata', 'assessment_id', 'status',
                'resolution', 'duplicate_id', 'location', 'additional_location_information', 'detail',
                'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'number_of_errors',
                'resource', 'accounts_link', 'file_1', 'file_2', 'archived']

    def get_readonly_fields(self, request, obj=None):
        if self._is_content_manager(request):
            return ['id', 'created', 'modified', 'accounts_link']
        elif self._is_editorial_vendor(request):
            return ['id', 'created', 'modified', 'accounts_user_faculty_status', 'archived', 'junk']
        return ['id', 'created', 'modified', 'book', 'is_assessment_errata', 'assessment_id', 'status',
                'resolution', 'duplicate_id', 'archived', 'location', 'additional_location_information', 'detail',
                'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'number_of_errors',
                'resource', 'accounts_link', 'file_1', 'file_2']

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.context_data['save_as'] = self._is_content_manager(request) or self._is_editorial_vendor(request)
        return response

admin.site.register(Errata, ErrataAdmin)
admin.site.register(BlockedUser, BlockedUserAdmin)
admin.site.register(EmailText)
