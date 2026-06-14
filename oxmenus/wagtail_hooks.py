from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from .admin_views import RegionCreateView, RegionIndexView, RegionReorderView
from .models import Menus


class BaseMenuViewSet(ModelViewSet):
    model = Menus
    icon = "list-ul"
    add_view_class = RegionCreateView
    index_view_class = RegionIndexView
    reorder_view_class = RegionReorderView
    # Native drag-and-drop reordering in the list, backed by sort_order.
    # Default list ordering comes from Menus.Meta.ordering (no explicit
    # ordering attr is set on the viewset itself).
    sort_order_field = "sort_order"
    list_display = ("name", "node_type_label", "sort_order", "feature_flag")
    search_fields = ("name",)
    region = None

    def get_index_view_kwargs(self, **kwargs):
        return super().get_index_view_kwargs(region=self.region, **kwargs)

    def get_add_view_kwargs(self, **kwargs):
        return super().get_add_view_kwargs(region=self.region, **kwargs)

    def get_reorder_view_kwargs(self, **kwargs):
        return super().get_reorder_view_kwargs(region=self.region, **kwargs)


class UtilityMenuViewSet(BaseMenuViewSet):
    menu_label = "Utility bar"
    region = "utility"


class MainMenuViewSet(BaseMenuViewSet):
    menu_label = "Main nav"
    region = "main"


class FooterMenuViewSet(BaseMenuViewSet):
    menu_label = "Footer"
    region = "footer"


class NavigationGroup(ModelViewSetGroup):
    menu_label = "Navigation"
    menu_icon = "list-ul"
    menu_order = 520
    items = (
        UtilityMenuViewSet("utility_menu"),
        MainMenuViewSet("main_menu"),
        FooterMenuViewSet("footer_menu"),
    )


@hooks.register("register_admin_viewset")
def register_navigation_group():
    return NavigationGroup()
