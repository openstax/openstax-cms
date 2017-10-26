from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', )
    list_display = ('user', 'uuid', 'faculty_status',)
    search_fields = ('uuid', 'user__username', 'user__email', 'user__last_name')
    list_filter = ('faculty_status', )

admin.site.register(Profile, ProfileAdmin)
