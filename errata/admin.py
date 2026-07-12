import unicodecsv
from import_export import resources
from import_export.admin import ExportActionMixin, ImportExportActionModelAdmin
from import_export.formats import base_formats
from import_export.fields import Field

from django.contrib import admin, messages
from django.contrib.admin.filters import RelatedFieldListFilter
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.http import HttpResponse
from django.urls import path
from django.utils.html import mark_safe

from rangefilter.filters import DateRangeFilter

from books.constants import RETIRED
from books.models import Book
from reversion.admin import VersionAdmin

from .models import Errata, BlockedUser, EmailText, InternalDocumentation
from .forms import ErrataForm
from . import views


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


class DefaultActiveQueueFilter(admin.SimpleListFilter):
    """Hides archived/junk noise by default so the changelist reads as a
    working queue, without breaking the existing archived/junk list_filter
    dropdowns - those still work for anyone who explicitly filters by them.
    ?view=all is the escape hatch back to an unfiltered list."""
    title = 'queue'
    parameter_name = 'view'

    def lookups(self, request, model_admin):
        return (('all', 'All (including archived/junk)'),)

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': 'Active queue',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset
        return queryset.filter(archived=False, junk=False)


class ErrataAdmin(ImportExportActionModelAdmin, VersionAdmin):
    def get_queryset(self, request):
        return super(ErrataAdmin, self).get_queryset(request).select_related('book')

    def get_urls(self):
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(views.errata_dashboard), name='errata_errata_dashboard'),
        ]
        return custom_urls + super().get_urls()

    change_list_template = 'admin/errata/errata/change_list.html'

    class Media:
        js = (
            'errata/errata-admin-ui.js',  # custom errata javascript (uses django.jQuery, already loaded by admin)
        )
    resource_class = ErrataResource
    ordering = ['created']

    form = ErrataForm
    list_max_show_all = 500
    list_per_page = 100
    save_as = True

    # Columns/filters aren't role-sensitive - accounts_link (the one FERPA-adjacent
    # field) never appears in the changelist, only on the add/change form.
    list_display = ['id', 'book_title', 'created', 'modified', 'short_detail', 'number_of_errors', 'status',
                     'error_type', 'resource', 'location', 'additional_location_information', 'resolution',
                     'archived', 'junk']
    list_display_links = ['book_title']
    list_filter = (DefaultActiveQueueFilter, ('created', DateRangeFilter), ('modified', DateRangeFilter),
                   ('book', ActiveBookListFilter), 'status', 'is_assessment_errata', 'error_type', 'resolution',
                   'archived', 'junk', 'resource')

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

    # Every field except accounts_link, for every role. Internal Editors (and
    # Super Admins) also see accounts_link - see get_fields/get_readonly_fields.
    FIELDS = ['id', 'created', 'modified', 'book', 'is_assessment_errata', 'assessment_id', 'status',
              'resolution', 'duplicate_id', 'location', 'additional_location_information', 'detail',
              'internal_notes', 'resolution_notes', 'resolution_date', 'error_type', 'number_of_errors',
              'resource', 'accounts_link', 'file_1', 'file_2', 'archived', 'junk']
    READONLY_FIELDS = ['id', 'created', 'modified', 'accounts_link']

    def get_export_formats(self):
        return [base_formats.CSV]

    """Actions for the Django Admin list view.

    These call .save() per object rather than queryset.update() - update()
    is a raw SQL UPDATE that never calls Errata.save() and never fires
    post_save, so it silently skipped date auto-stamping, resolution_notes
    autofill, the reporter-notification email, and clean()'s
    resolution-required rule. Objects that fail that validation (e.g. no
    resolution set yet) are left untouched and reported back to the user
    instead of being forced into an inconsistent state.
    """
    def _apply_bulk_change(self, request, queryset, label, **field_updates):
        updated = 0
        skipped = []
        for obj in queryset:
            for field, value in field_updates.items():
                setattr(obj, field, value)
            try:
                obj.clean()
            except ValidationError as e:
                skipped.append('#{}: {}'.format(obj.pk, e.messages[0]))
                continue
            obj.save()
            updated += 1

        if skipped:
            self.message_user(
                request,
                '{}: {} updated, {} skipped - {}'.format(label, updated, len(skipped), '; '.join(skipped)),
                level=messages.WARNING,
            )
        else:
            self.message_user(request, '{}: {} updated.'.format(label, updated))

    def mark_in_review(self, request, queryset):
        self._apply_bulk_change(request, queryset, 'Mark as Editorial Review', status='Editorial Review')
    mark_in_review.short_description = "Mark errata as Editorial Review"

    def mark_OpenStax_editorial_review(self, request, queryset):
        self._apply_bulk_change(request, queryset, 'Mark as OpenStax Editorial Review', status='OpenStax Editorial Review')
    mark_OpenStax_editorial_review.short_description = "Mark errata as OpenStax Editorial Review"

    def mark_cartridge_review(self, request, queryset):
        self._apply_bulk_change(request, queryset, 'Mark as Cartridge Review', status='Cartridge Review')
    mark_cartridge_review.short_description = "Mark errata as cartridge review"

    def mark_reviewed(self, request, queryset):
        self._apply_bulk_change(request, queryset, 'Mark as Reviewed', status='Reviewed')
    mark_reviewed.short_description = "Mark errata as reviewed"

    def mark_archived(self, request, queryset):
        self._apply_bulk_change(request, queryset, 'Mark as archived', archived=True)
    mark_archived.short_description = "Mark errata as archived"

    def mark_completed(self, request, queryset):
        self._apply_bulk_change(request, queryset, 'Mark as Completed', status='Completed')
    mark_completed.short_description = "Mark errata as completed"

    def get_actions(self, request):
        # delete_selected is handled by Django's own has_delete_permission
        # (default implementation already checks request.user.has_perm
        # ('errata.delete_errata') - no override needed here). Only the
        # custom bulk status actions need manual gating, since they don't
        # carry an allowed_permissions attribute for Django to check itself.
        actions = super(ErrataAdmin, self).get_actions(request)
        if not self._is_internal_editor(request):
            for action_name in ('mark_in_review', 'mark_OpenStax_editorial_review', 'mark_cartridge_review',
                                'mark_reviewed', 'mark_archived', 'mark_completed'):
                actions.pop(action_name, None)
        return actions

    # To enable sorting by book title on the admin page, computing field using a method
    def book_title(self, obj):
        return mark_safe(obj.book.title)

    book_title.admin_order_field = 'book__title'

    """Model permissions"""
    # ErrataAdmin is a single instance shared across all requests, so per-request
    # field lists must be computed and returned (get_fields, get_readonly_fields)
    # rather than assigned to self - mutating self.* here raced across
    # concurrent requests from different user roles and produced "Unknown
    # field(s) specified for Errata" 500s (Sentry OPENSTAX-CMS-VJ/VH).
    #
    # Only one role distinction remains: Internal Editor (superuser or
    # 'Content Managers' group) vs. everyone else. "Everyone else" is treated
    # as Editorial Vendor tier as a least-privilege default, not just the
    # explicit 'Editorial Vendor' group - see
    # docs/superpowers/specs/2026-07-10-errata-admin-permissions-design.md.
    def _is_internal_editor(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Content Managers']).exists()

    def get_fields(self, request, obj=None):
        fields = list(self.FIELDS)
        if not self._is_internal_editor(request):
            fields.remove('accounts_link')
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.READONLY_FIELDS)
        if not self._is_internal_editor(request):
            readonly_fields.remove('accounts_link')
        return readonly_fields

admin.site.register(Errata, ErrataAdmin)
admin.site.register(BlockedUser, BlockedUserAdmin)
admin.site.register(EmailText)
