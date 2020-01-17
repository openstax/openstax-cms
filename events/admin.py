from django.contrib import admin

from .models import Event, Session, Registration

# class SessionAdmin(admin.ModelAdmin):
#     list_display = ['name', 'phone']
#     list_filter = ('key_institutional_partner', 'achieving_the_dream_school', 'hbcu', 'texas_higher_ed')
#     search_fields = ['name', ]
#
#     def has_add_permission(self, request):
#         return False

#admin.site.register(Partner, PartnerAdmin)
admin.site.register(Event)
admin.site.register(Session)
admin.site.register(Registration)