from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from .models import Webinar

class WebinarAdmin(ModelAdmin):
    model = Webinar
    menu_icon = 'media'
    menu_label = 'Webinars'
    menu_order = 4000
    list_display = ('title', 'start', 'end', 'spaces_remaining')
    search_fields = ('title')

modeladmin_register(WebinarAdmin)
