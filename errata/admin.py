import unicodecsv
from import_export import resources
from import_export.admin import ExportActionModelAdmin

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


class ErrataResource(resources.ModelResource):
    class Meta:
        model = Errata
        fields = ('id', 'created', 'modified', 'book__title', 'is_assessment_errata', 'assessment_id', 'status', 'resolution', 'archived', 'location', 'detail', 'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'resource', 'submitted_by_account_id')
        export_order = ('id', 'created', 'modified', 'book__title', 'is_assessment_errata', 'assessment_id', 'status', 'resolution', 'archived', 'location', 'detail', 'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'resource', 'submitted_by_account_id')


class InlineInternalImage(admin.TabularInline):
    model = InternalDocumentation


class ErrataAdmin(ExportActionModelAdmin):
    resource_class = ErrataResource

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
    actions = ['mark_in_review', 'mark_reviewed', 'mark_archived']
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
                           'user_email',
                           'accounts_link',
                           'file_1',
                           'file_2'] # fields to show on the actual form
            self.readonly_fields = ['id',
                                    'created',
                                    'modified',
                                    'user_email',
                                    'accounts_link']
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
                           'user_email',
                           'accounts_link',
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
                                    'user_email',
                                    'accounts_link',
                                    'file_1',
                                    'file_2']
            self.save_as = False

        return super(ErrataAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Errata, ErrataAdmin)
