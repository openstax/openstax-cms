from django.contrib import admin
from .models import OpenStaxUserProfile

class OpenStaxUserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'openstax_accounts_uuid']
    search_fields = ['user', 'openstax_accounts_uuid' ]
    raw_id_fields = ['user']

    def has_add_permission(self, request):
        return False

admin.site.register(OpenStaxUserProfile, OpenStaxUserProfileAdmin)
