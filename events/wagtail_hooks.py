from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Event, Session, Registration


class SessionAdmin(ModelAdmin):
    model = Session
    menu_label = 'CF Sessions'
    menu_icon = 'date'
    menu_order = 2000
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('name', 'date' ,'seats_remaining')
    search_fields = ('name',)

modeladmin_register(SessionAdmin)
