from django.contrib import admin
from .models import CustomizationRequest

class CustomizationRequestAdmin(admin.ModelAdmin):
    list_display = ['email', 'num_students', "reason", "modules"]
    search_fields = ['email', ]

    def has_add_permission(self, request):
        return False

admin.site.register(CustomizationRequest, CustomizationRequestAdmin)
