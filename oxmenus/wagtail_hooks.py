from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from .models import Menus


class OXMenusAdmin(ModelAdmin):
    model = Menus
    menu_icon = 'media'
    menu_label = 'OX Menu'
    menu_order = 5000
    list_display = ('name',)
    search_fields = ('name',) # trailing comma needed to make search work


modeladmin_register(OXMenusAdmin)
