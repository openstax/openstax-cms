import unicodecsv

from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.html import mark_safe

from extraadminfilters.filters import UnionFieldListFilter

from .models import Errata, InternalDocumentation
from .forms import ErrataForm


class InlineInternalImage(admin.TabularInline):
    model = InternalDocumentation


class ErrataAdmin(admin.ModelAdmin):
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
              'location',
              'detail',
              'internal_notes',
              'resolution_notes',
              'resolution_date',
              'error_type',
              'number_of_errors',
              'resource',
              'submitted_by',
              'submitter_email_address',
              'submitted_by_account_id',
              'file_1',
              'file_2']
    search_fields = ('id',
                     'book__title',
                     'detail',
                     'location',
                     'submitted_by__first_name',
                     'submitted_by__last_name',
                     'submitted_by__email')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    actions = ['mark_in_review', 'mark_reviewed', 'mark_archived', 'export_as_csv']
    inlines = [InlineInternalImage, ]
    raw_id_fields = ('submitted_by', 'duplicate_id')

    """Actions for the Django Admin list view"""
    def mark_in_review(self, request, queryset):
        queryset.update(status='Editorial Review')
    mark_in_review.short_description = "Mark errata as in-review"

    def mark_reviewed(self, request, queryset):
        queryset.update(status='Reviewed')
    mark_reviewed.short_description = "Mark errata as reviewed"

    def mark_archived(self, request, queryset):
        queryset.update(archived=True)
    mark_archived.short_description = "Mark errata as archived"

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format("file1")

        writer = unicodecsv.writer(response, encoding='utf-8')
        writer.writerow([
            smart_str("Errata ID"),
            smart_str("Created"),
            smart_str("Modified"),
            smart_str("Book"),
            smart_str("Assessment"),
            smart_str("Assessment ID"),
            smart_str("Status"),
            smart_str("Resolution"),
            smart_str("Archived"),
            smart_str("Location"),
            smart_str("Detail"),
            smart_str("Internal Notes"),
            smart_str("Resolution Notes"),
            smart_str("Resolution Date"),
            smart_str("Error Type"),
            smart_str("Resource"),
            smart_str("Submitted By"),
            smart_str("Submitter E-mail Address"),
            smart_str("Submitted By Group(s)"),
        ])
        for obj in queryset:
            groups = []
            if obj.submitted_by:
                for group in obj.submitted_by.groups.all():
                    groups.append(group.name)

            writer.writerow([
                smart_str(obj.pk),
                smart_str(obj.created),
                smart_str(obj.modified),
                smart_str(obj.book.title),
                smart_str(obj.is_assessment_errata),
                smart_str(obj.assessment_id),
                smart_str(obj.status),
                smart_str(obj.resolution),
                smart_str(obj.archived),
                smart_str(obj.location),
                smart_str(obj.detail),
                smart_str(obj.internal_notes),
                smart_str(obj.resolution_notes),
                smart_str(obj.resolution_date),
                smart_str(obj.error_type),
                smart_str(obj.resource),
                smart_str(obj.submitted_by),
                smart_str(obj.submitter_email_address),
                smart_str(''.join(groups))
            ])
        return response
    export_as_csv.short_description = "Export as CSV file"

    def get_actions(self, request):
        actions = super(ErrataAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def change_view(self, request, object_id, extra_context=None):
        if not request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers', 'Content Development Intern']).exists():
            extra_context = extra_context or {}
            extra_context['readonly'] = True
        return super(ErrataAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def _book_title(self, obj):
        return mark_safe(obj.book.title)

    """Model permissions"""
    @method_decorator(csrf_protect)
    def changelist_view(self, request, extra_context=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers', 'Content Development Intern']).exists():
            self.list_display = ['id', '_book_title', 'created', 'is_assessment_errata', 'short_detail', 'status', 'error_type', 'resource', 'location', 'resolution', 'archived'] # list of fields to show if user can't approve the post
            self.list_display_links = ['_book_title']
            self.list_filter = (('book', UnionFieldListFilter), 'status', 'created', 'is_assessment_errata', 'modified', 'error_type', 'resolution', 'archived', 'resource')
            self.editable = ['resolution']
        else:
            self.list_display = ['id', '_book_title', 'created', 'is_assessment_errata', 'short_detail', 'status', 'error_type', 'resource', 'location', 'created', 'archived'] # list of fields to show if user can approve the post
            self.list_display_links = ['_book_title']
            self.list_filter = (('book', UnionFieldListFilter), 'status', 'created', 'modified', 'is_assessment_errata', 'error_type', 'resolution', 'archived', 'resource')
        return super(ErrataAdmin, self).changelist_view(request, extra_context)

    @method_decorator(csrf_protect)
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers', 'Content Development Intern']).exists():
            self.fields = ['id',
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
                           'detail',
                           'internal_notes',
                           'resolution_notes',
                           'resolution_date',
                           'error_type',
                           'number_of_errors',
                           'resource',
                           'submitted_by',
                           'submitter_email_address',
                           'submitted_by_account_id',
                           'file_1',
                           'file_2'] # fields to show on the actual form
            self.readonly_fields = ['id',
                                    'created',
                                    'modified']
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
                           'archived',
                           'location',
                           'detail',
                           'internal_notes',
                           'resolution_notes',
                           'resolution_date',
                           'error_type',
                           'number_of_errors',
                           'resource',
                           'submitted_by',
                           'submitter_email_address',
                           'submitted_by_account_id',
                           'file_1',
                           'file_2']
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
                                    'detail',
                                    'internal_notes',
                                    'resolution_notes',
                                    'resolution_date',
                                    'error_type',
                                    'number_of_errors',
                                    'resource',
                                    'submitted_by',
                                    'submitter_email_address',
                                    'submitted_by_account_id',
                                    'file_1',
                                    'file_2']
            self.save_as = False

        return super(ErrataAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Errata, ErrataAdmin)
