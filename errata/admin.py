import unicodecsv
from import_export import resources
from import_export.admin import ExportActionMixin, ImportExportActionModelAdmin
from import_export.formats import base_formats
from import_export.fields import Field

from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.utils.html import mark_safe

from rangefilter.filters import DateRangeFilter

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

class ErrataAdmin(ImportExportActionModelAdmin, VersionAdmin):
    def get_queryset(self, request):
        return super(ErrataAdmin, self).get_queryset(request).prefetch_related('book')

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

    fields = ['id',
              'created',
              'modified',
              'book',
              'is_assessment_errata',
              'assessment_id',
              'status',
              'resolution',
              'duplicate_id',
              'archived',
              'junk',
              'location',
              'additional_location_information',
              'detail',
              'internal_notes',
              'resolution_notes',
              'resolution_date',
              'error_type',
              'number_of_errors',
              'resource',
              'file_1',
              'file_2']
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
    @method_decorator(csrf_protect)
    def changelist_view(self, request, extra_context=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers']).exists():
            self.list_display = ['id', 'book_title', 'created', 'modified', 'short_detail', 'number_of_errors', 'status', 'error_type', 'resource', 'location', 'additional_location_information', 'resolution', 'archived', 'junk'] # list of fields to show if user is in Content Manager group or is a superuser
            self.list_display_links = ['book_title']
            self.list_filter = (('created', DateRangeFilter), ('modified', DateRangeFilter), 'book', 'status', 'created', 'modified', 'is_assessment_errata', 'modified', 'error_type', 'resolution', 'archived', 'junk', 'resource')
            self.editable = ['resolution']

        else:
            self.list_display = ['id', 'book_title', 'created', 'short_detail', 'status', 'error_type', 'resource', 'location', 'created', 'archived'] # list of fields to show otherwise
            self.list_display_links = ['book_title']
            self.list_filter = (('created', DateRangeFilter), ('modified', DateRangeFilter), 'book', 'status', 'created', 'modified', 'is_assessment_errata', 'error_type', 'resolution', 'archived', 'resource')
        return super(ErrataAdmin, self).changelist_view(request, extra_context)

    @method_decorator(csrf_protect)
    def get_form(self, request, obj=None, **kwargs):
        # CONTENT MANAGERS AND ADMINS
        if request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers']).exists():
            self.fields = ['id',
                           'created',
                           'modified',
                           'book',
                           'is_assessment_errata',
                           'assessment_id',
                           'status',
                           'resolution',
                           'duplicate_id',
                           'location',
                           'additional_location_information',
                           'detail',
                           'internal_notes',
                           'resolution_notes',
                           'resolution_date',
                           'error_type',
                           'number_of_errors',
                           'resource',
                           'accounts_link',
                           'file_1',
                           'file_2',
                           'archived',
                           'junk',
                           ] # fields to show on the actual form
            self.readonly_fields = ['id',
                                    'created',
                                    'modified',
                                    'accounts_link',
                                    ]

            self.save_as = True
        elif request.user.groups.filter(name__in=['Editorial Vendor']).exists():
            self.fields = ['id',
                           'created',
                           'modified',
                           'book',
                           'is_assessment_errata',
                           'assessment_id',
                           'status',
                           'resolution',
                           'duplicate_id',
                           'location',
                           'additional_location_information',
                           'detail',
                           'internal_notes',
                           'resolution_notes',
                           'resolution_date',
                           'error_type',
                           'number_of_errors',
                           'resource',
                           'accounts_user_faculty_status',
                           'file_1',
                           'file_2',
                           'archived',
                            ]  # fields to show on the actual form
            self.readonly_fields = ['id',
                                    'created',
                                    'modified',
                                    'accounts_user_faculty_status',
                                    'archived',
                                    'junk',
                                    ]

            self.save_as = True
        else:
            self.fields = ['id',
                           'created',
                           'modified',
                           'book',
                           'is_assessment_errata',
                           'assessment_id',
                           'status',
                           'resolution',
                           'duplicate_id',
                           'location',
                           'additional_location_information',
                           'detail',
                           'internal_notes',
                           'resolution_notes',
                           'resolution_date',
                           'error_type',
                           'number_of_errors',
                           'resource',
                           'accounts_link',
                           'file_1',
                           'file_2',
                           'archived',
                           ]
            self.readonly_fields = ['id',
                                    'created',
                                    'modified',
                                    'book',
                                    'is_assessment_errata',
                                    'assessment_id',
                                    'status',
                                    'resolution',
                                    'duplicate_id',
                                    'archived',
                                    'location',
                                    'additional_location_information',
                                    'detail',
                                    'internal_notes',
                                    'resolution_notes',
                                    'resolution_date',
                                    'error_type',
                                    'number_of_errors',
                                    'resource',
                                    'accounts_link',
                                    'file_1',
                                    'file_2',
                                    ]
            self.save_as = False

        return super(ErrataAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Errata, ErrataAdmin)
admin.site.register(BlockedUser, BlockedUserAdmin)
admin.site.register(EmailText)
