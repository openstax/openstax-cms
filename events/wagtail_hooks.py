from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from wagtail.admin.menu import MenuItem
from .models import Session, Event, Registration


class EventAdmin(ModelAdmin):
    model = Event
    menu_label = 'Event Admin'  # ditch this to use verbose_name_plural from model
    menu_order = 1000
    menu_icon = 'list-ul'  # change as required
    list_display = ('eventbrite_event_id', )
    search_fields = ('eventbrite_event_id',)


class SessionAdmin(ModelAdmin):
    model = Session
    menu_label = 'Session Admin'
    menu_icon = 'date'
    menu_order = 2000
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('name', 'date' ,'seats_remaining')
    search_fields = ('name',)


class RegistrationAdmin(ModelAdmin):
    model = Registration
    menu_label = 'Registrations'  # ditch this to use verbose_name_plural from model
    menu_icon = 'group'  # change as required
    list_display = ('full_name', 'registration_email', 'checked_in')
    search_fields = ('last_name', 'registration_email')
    list_filter = ['session', ]


class EventAdminGroup(ModelAdminGroup):
    menu_label = 'Creator Fest'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 2000  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (SessionAdmin, EventAdmin)

    def get_submenu_items(self):
        menu_items = []
        item_order = 1
        for modeladmin in self.modeladmin_instances:
            menu_items.append(modeladmin.get_menu_item(order=item_order))
            item_order += 1
        menu_items.append(MenuItem('Registrations', '/django-admin/events/registration/', classnames='icon icon-group', order=3000))
        return menu_items

modeladmin_register(EventAdminGroup)