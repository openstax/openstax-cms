import unicodecsv

from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.utils.encoding import smart_str

from .models import Errata, Resource, ErrorType


class ErrataAdmin(admin.ModelAdmin):
    fields = ['created',
              'modified',
              'book',
              'status',
              'resolution',
              'archived',
              'location',
              'detail',
              'resolution_notes',
              'resolution_date',
              'internal_notes',
              'error_type',
              'resource',
              'submitter_email_address']
    radio_fields = {'book': admin.HORIZONTAL}
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    actions = ['mark_in_review', 'mark_approved', 'mark_archived', 'export_as_csv']

    """Actions for the Django Admin list view"""
    def mark_in_review(self, request, queryset):
        queryset.update(status='R')
    mark_in_review.short_description = "Mark errata as In Review"

    def mark_approved(self, request, queryset):
        queryset.update(status='A')
    mark_approved.short_description = "Mark errata as Approved"

    def mark_archived(self, request, queryset):
        queryset.update(archived=True)
    mark_archived.short_description = "Mark errata as Archived"

    def export_as_csv(self, request, queryset):
        # we should use this instead of retyping all the fields
        #field_names = self.fields

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format("file1")

        writer = unicodecsv.writer(response, encoding='utf-8')
        writer.writerow([
            smart_str("ID"),
            smart_str("Created"),
            smart_str("Modified"),
            smart_str("Book"),
            smart_str("Status"),
            smart_str("Resolution"),
            smart_str("Archived"),
            smart_str("Location"),
            smart_str("Detail"),
            smart_str("Resolution Notes"),
            smart_str("Resolution Date"),
            smart_str("Internal Notes"),
            smart_str("Error Type"),
            smart_str("Resource"),
            smart_str("Submitter E-mail Address"),
        ])
        for obj in queryset:
            writer.writerow([
                smart_str(obj.pk),
                smart_str(obj.created),
                smart_str(obj.modified),
                smart_str(obj.book.title),
                smart_str(obj.status),
                smart_str(obj.resolution),
                smart_str(obj.archived),
                smart_str(obj.location),
                smart_str(obj.detail),
                smart_str(obj.resolution_notes),
                smart_str(obj.resolution_date),
                smart_str(obj.internal_notes),
                smart_str(obj.error_type),
                smart_str(obj.resource),
                smart_str(obj.submitter_email_address),
            ])
        return response
    export_as_csv.short_description = "export as csv"

    def get_actions(self, request):
        actions = super(ErrataAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def change_view(self, request, object_id, extra_context=None):
        if not request.user.is_superuser:
            extra_context = extra_context or {}
            extra_context['readonly'] = True
        return super(ErrataAdmin, self).change_view(request, object_id, extra_context=extra_context)

    """Model permissions"""
    @method_decorator(csrf_protect)
    def changelist_view(self, request, extra_context=None):
        if request.user.is_superuser:
            self.list_display = ['id', 'book', 'status', 'error_type', 'resources', 'resolution', 'archived'] # list of fields to show if user can't approve the post
            self.list_display_links = ['book']
            self.list_filter = ('book', 'status', 'created', 'modified', 'error_type', 'archived')
            self.editable = ['resolution']
        else:
            self.list_display = ['id', 'book', 'status', 'error_type', 'resource', 'created', 'archived'] # list of fields to show if user can approve the post
            self.list_display_links = ['book']
            self.list_filter = ('book', 'status', 'created', 'modified', 'error_type', 'archived')
        return super(ErrataAdmin, self).changelist_view(request, extra_context)

    @method_decorator(csrf_protect)
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            self.fields = ['created',
                           'modified',
                           'book',
                           'status',
                           'resolution',
                           'archived',
                           'location',
                           'detail',
                           'resolution_notes',
                           'resolution_date',
                           'internal_notes',
                           'error_type',
                           'resource',
                           'submitter_email_address'] # fields to show on the actual form
            self.readonly_fields = ['created',
                                    'modified']
            self.save_as = True
        else:
            self.fields = ['created',
                           'modified',
                           'book',
                           'status',
                           'resolution',
                           'archived',
                           'location',
                           'detail',
                           'resolution_notes',
                           'resolution_date',
                           'internal_notes',
                           'error_type',
                           'resource',
                           'submitter_email_address']
            self.readonly_fields = ['created',
                                    'modified',
                                    'book',
                                    'status',
                                    'resolution',
                                    'archived',
                                    'location',
                                    'detail',
                                    'resolution_notes',
                                    'resolution_date',
                                    'internal_notes',
                                    'error_type',
                                    'resource',
                                    'submitter_email_address']
            self.save_as = False

        return super(ErrataAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Errata, ErrataAdmin)
admin.site.register(Resource)
admin.site.register(ErrorType)
