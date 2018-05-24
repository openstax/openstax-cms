from django.contrib import admin

from .models import School


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    list_filter = ('key_institutional_partner', 'achieving_the_dream_school', 'hbcu', 'texas_higher_ed')

admin.site.register(School, SchoolAdmin)