from django.contrib import admin

from .models import Event, Session, Registration

class SessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'seats_remaining']
    list_filter = ('location', 'date')
    search_fields = ['name', ]


admin.site.register(Event)
admin.site.register(Session, SessionAdmin)
admin.site.register(Registration)
