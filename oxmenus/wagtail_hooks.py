from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Menus


class OXMenusViewSet(ModelViewSet):
    model = Menus
    icon = "grip"
    menu_label = "OX Menu"
    menu_order = 520
    add_to_admin_menu = True
    list_display = ("name", "sort_order", "key", "feature_flag")
    ordering = ("sort_order", "id")
    search_fields = ("name",)
    exclude_form_fields = []


@hooks.register("register_admin_viewset")
def register_oxmenus_viewset():
    return OXMenusViewSet("oxmenus")
