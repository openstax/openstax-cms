from django.contrib import admin

from .models import Event, Session, Registration


admin.site.register(Event)
admin.site.register(Session)
admin.site.register(Registration)
