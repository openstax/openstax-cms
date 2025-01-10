from django.contrib import admin
from django.core import management

from .models import AdoptionOpportunityRecord, \
    School, \
    MapBoxDataset, \
    SalesforceSettings, \
    SalesforceForms, \
    Partner, \
    PartnerCategoryMapping, \
    PartnerFieldNameMapping, \
    PartnerTypeMapping, \
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


class PartnerAdmin(admin.ModelAdmin):
    list_display = ['partner_logo_tag', 'partner_name', 'partner_type', 'visible_on_website']
    list_display_links = ('partner_name', )
    list_filter = ('visible_on_website', 'partner_type')
    search_fields = ('partner_name', 'salesforce_id')
    readonly_fields = ('salesforce_id', 'account_id', 'partner_status', 'partnership_level', 'equity_rating', 'partner_sf_account_id', 'affordability_cost', 'books', 'partner_type')

    actions = ['sync_with_salesforce', 'mark_visible', 'mark_not_visible']

    def sync_with_salesforce(self, request, queryset):
        management.call_command('update_partners', verbosity=0)
    sync_with_salesforce.short_description = "Sync Partners with Salesforce"
    sync_with_salesforce.allowed_permissions = ('change',)

    def mark_visible(self, request, queryset):
        queryset.update(visible_on_website=True)
    mark_visible.short_description = "Mark partners as visible on website"
    mark_visible.allowed_permissions = ('change',)

    def mark_not_visible(self, request, queryset):
        queryset.update(visible_on_website=False)
    mark_not_visible.short_description = "Mark partners as not visible on website"
    mark_not_visible.allowed_permissions = ('change',)

    def save_model(self, request, obj, form, change):
        obj.from_admin_site = True
        super().save_model(request, obj, form, change)


class PartnerCategoryMappingAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'salesforce_name')


class PartnerFieldNameMappingAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'salesforce_name')


class PartnerTypeMappingAdmin(admin.ModelAdmin):
    list_display = ('display_name',)


class ResourceDownloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'last_access', 'resource_name', 'book', 'book_format', 'account_uuid')
    list_filter = ('created', 'book')


admin.site.register(SalesforceSettings, SalesforceSettingsAdmin)
admin.site.register(SalesforceForms, SalesforceFormsAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(AdoptionOpportunityRecord, AdoptionOpportunityRecordAdmin)
admin.site.register(MapBoxDataset)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(PartnerCategoryMapping, PartnerCategoryMappingAdmin)
admin.site.register(PartnerFieldNameMapping, PartnerFieldNameMappingAdmin)
admin.site.register(PartnerTypeMapping, PartnerTypeMappingAdmin)
admin.site.register(ResourceDownload, ResourceDownloadAdmin)
admin.site.register(SavingsNumber)
