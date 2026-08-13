from django.contrib import admin

from .models import AdoptionOpportunityRecord, \
    School, \
    MapBoxDataset, \
    SalesforceSettings, \
    SalesforceForms, \
    ResourceDownload, \
    SavingsNumber


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'salesforce_id', 'type', 'current_year_students', 'total_school_enrollment', 'updated']
    list_filter = ('type', 'location', 'updated')
    search_fields = ['name', ]

    def has_add_permission(self, request):
        return False


class AdoptionOpportunityRecordAdmin(admin.ModelAdmin):
    list_display = ['account_uuid', 'book_name', 'students', 'savings']
    list_filter = ('book_name', 'created', 'opportunity_stage')
    search_fields = ['account_uuid', 'opportunity_id']
    readonly_fields = [
        'opportunity_id',
        'opportunity_stage',
        'account_uuid',
        'adoption_type',
        'base_year',
        'confirmation_date',
        'confirmation_type',
        'how_using',
        'savings',
        'students',
        'book_name',
        'created'
    ]

    def has_add_permission(self, request):
        return False


class SalesforceSettingsAdmin(admin.ModelAdmin):
    # only allow one SF Setting to exist
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class SalesforceFormsAdmin(admin.ModelAdmin):
    # only allow one SF Setting to exist
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class ResourceDownloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'last_access', 'resource_name', 'book', 'book_format', 'account_uuid')
    list_filter = ('created', 'book')


admin.site.register(SalesforceSettings, SalesforceSettingsAdmin)
admin.site.register(SalesforceForms, SalesforceFormsAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(AdoptionOpportunityRecord, AdoptionOpportunityRecordAdmin)
admin.site.register(MapBoxDataset)
admin.site.register(ResourceDownload, ResourceDownloadAdmin)
admin.site.register(SavingsNumber)
