from django.urls import reverse

from wagtail import hooks
from wagtail.admin.views import generic
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from global_settings.models import Footer
from global_settings.menu import SettingsLinkMenuItem
from .models import Menus


class _PlacementScopedCreateView(generic.CreateView):
    """Sets a new row's `placement` from whichever nav this viewset manages.

    `placement` is kept out of the form entirely, so it is set here rather than
    defaulted: an editable field would let someone move a row into the other nav,
    where it would vanish from this list and be served by the wrong menu.
    """

    placement = None

    def save_instance(self):
        self.form.instance.placement = self.placement
        return super().save_instance()


class _PlacementScopedMenusViewSet(ModelViewSet):
    """Common base for the Header/Footer Menus viewsets: same model, same admin
    behaviour, scoped to one `placement` value."""

    model = Menus
    icon = "grip"
    menu_label = "Menus"
    list_display = ("name", "sort_order", "key", "feature_flag")
    ordering = ("sort_order", "id")
    search_fields = ("name",)
    exclude_form_fields = ["placement"]
    placement = None

    def get_common_view_kwargs(self, **kwargs):
        return super().get_common_view_kwargs(
            queryset=Menus.objects.filter(placement=self.placement), **kwargs
        )


class HeaderMenusCreateView(_PlacementScopedCreateView):
    placement = 'header'


class FooterMenusCreateView(_PlacementScopedCreateView):
    placement = 'footer'


class HeaderMenusViewSet(_PlacementScopedMenusViewSet):
    name = "headermenus"
    menu_name = "headermenus"
    placement = 'header'
    add_view_class = HeaderMenusCreateView


class FooterMenusViewSet(_PlacementScopedMenusViewSet):
    name = "footermenus"
    menu_name = "footermenus"
    placement = 'footer'
    add_view_class = FooterMenusCreateView


class HeaderMenusGroup(ModelViewSetGroup):
    menu_label = "Header"
    menu_icon = "grip"
    menu_order = 240
    items = (HeaderMenusViewSet,)


class FooterMenusGroup(ModelViewSetGroup):
    menu_label = "Footer"
    menu_icon = "grip"
    menu_order = 250
    items = (FooterMenusViewSet,)

    def get_submenu_items(self):
        # Footer Content (the Footer site setting) is a Footer concern, not its own
        # viewset, so it belongs here rather than as a loose top-level entry.
        menu_items = super().get_submenu_items()
        menu_items.append(
            SettingsLinkMenuItem(
                "Footer Content", Footer, name="footer-content-settings",
                icon_name="cog", order=len(menu_items) + 1,
            )
        )
        return menu_items


@hooks.register("register_admin_viewset")
def register_header_menus_group():
    return HeaderMenusGroup()


@hooks.register("register_admin_viewset")
def register_footer_menus_group():
    return FooterMenusGroup()


@hooks.register("construct_settings_menu")
def remove_footer_from_settings(request, menu_items):
    # Footer is reachable from the Footer group, which is where everything else
    # about the footer now lives, so a second entry here is just another place to
    # look. The settings page itself is unchanged; only this menu entry goes.
    menu_items[:] = [item for item in menu_items if item.name != "footer"]
