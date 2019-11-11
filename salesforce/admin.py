from django.contrib import admin

from .models import AdoptionOpportunityRecord, School, MapBoxDataset, SalesforceSettings, Partner


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    list_filter = ('key_institutional_partner', 'achieving_the_dream_school', 'hbcu', 'texas_higher_ed')
    search_fields = ['name', ]

    def has_add_permission(self, request):
        return False

class AdoptionOpportunityRecordAdmin(admin.ModelAdmin):
    list_display = ['email', 'book_name', 'school', 'yearly_students']
    list_filter = ('book_name', 'school')
    search_fields = ['email', 'account_id']

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

class PartnerAdmin(admin.ModelAdmin):
    list_display = ['salesforce_id', 'partner_name', 'partner_type']


admin.site.register(SalesforceSettings, SalesforceSettingsAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(AdoptionOpportunityRecord, AdoptionOpportunityRecordAdmin)
admin.site.register(MapBoxDataset)
admin.site.register(Partner, PartnerAdmin)
