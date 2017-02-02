from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from .models import Errata


class ErrataAdmin(ModelAdmin):
    model = Errata
    menu_label = 'Errata Manager'  # ditch this to use verbose_name_plural from model
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    list_display = ('id', 'book', 'error_type', 'created')
    list_filter = ('resource', 'book', 'error_type', 'created', 'modified')
    search_fields = ('detail',)


class ErrataAdminGroup(ModelAdminGroup):
    menu_label = 'Errata'
    menu_icon = 'openquote'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (ErrataAdmin, )

# Now you just need to register your customised ModelAdmin class with Wagtail
#modeladmin_register(ErrataAdminGroup)
