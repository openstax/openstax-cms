from django.urls import reverse

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.views import generic
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from global_settings.models import Footer
from .models import Menus


class _PlacementScopedCreateView(generic.CreateView):
    """Defaults a new row's `placement` to whichever nav this viewset manages, so
    an editor adding a row under Header/Footer gets a row for that nav."""

    placement = None

    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault('placement', self.placement)
        return initial


class _PlacementScopedMenusViewSet(ModelViewSet):
    """Common base for the Header/Footer Menus viewsets: same model, same admin
    behaviour, scoped to one `placement` value."""

    model = Menus
    icon = "grip"
    menu_label = "Menus"
    list_display = ("name", "sort_order", "key", "feature_flag")
    ordering = ("sort_order", "id")
    search_fields = ("name",)
    exclude_form_fields = []
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


class SettingsLinkMenuItem(MenuItem):
    """Deep-links a BaseSiteSetting, hidden from users who cannot change it.

    Wagtail's own SettingMenuItem does the permission check but derives its label
    from the model's verbose_name; this needs a label of its own ("Footer Content"
    rather than "Footer", to read clearly nested under the Footer admin group).
    """

    def __init__(self, label, model, **kwargs):
        self.permission_policy = model.get_permission_policy()
        super().__init__(
            label,
            reverse("wagtailsettings:edit", args=(model._meta.app_label, model._meta.model_name)),
            **kwargs,
        )

    def is_shown(self, request):
        return self.permission_policy.user_has_permission(request.user, "change")


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
