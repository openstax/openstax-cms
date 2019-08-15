from django.contrib import admin

from .models import School, MapBoxDataset, SalesforceSettings


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    list_filter = ('key_institutional_partner', 'achieving_the_dream_school', 'hbcu', 'texas_higher_ed')
    search_fields = ['name', ]


class SalesforceSettingsAdmin(admin.ModelAdmin):
    # only allow one SF Setting to exist
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


admin.site.register(SalesforceSettings, SalesforceSettingsAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(MapBoxDataset)
