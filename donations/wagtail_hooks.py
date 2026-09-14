from django.urls import reverse

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from global_settings.models import GiveToday
from .models import DonationPopup, DonationLink, Fundraiser, SiteBanner


class DonationPopupViewSet(ModelViewSet):
    model = DonationPopup
    icon = "form"
    menu_label = "Donation Popup"
    list_display = ("download_ready", "header_title", "hide_donation_popup")
    search_fields = ("header_title", "header_subtitle", "download_ready")
    exclude_form_fields = []


class DonationLinkViewSet(ModelViewSet):
    model = DonationLink
    icon = "link-external"
    menu_label = "Donation Links"
    list_display = ("placement", "variant", "url", "is_active")
    list_filter = ("placement", "is_active")
    search_fields = ("variant", "url")
    exclude_form_fields = []


class FundraiserViewSet(ModelViewSet):
    model = Fundraiser
    icon = "site"
    menu_label = "Fundraisers"
    list_display = ("headline", "color_scheme", "message_type", "goal_amount", "goal_time")
    search_fields = ("headline", "message")
    exclude_form_fields = []


class SiteBannerViewSet(ModelViewSet):
    model = SiteBanner
    icon = "doc-full-inverse"
    menu_label = "Site Banners"
    list_display = ("name", "is_active", "start_date", "end_date", "context_filter")
    list_filter = ("is_active", "context_filter")
    search_fields = ("name", "html_message")
    exclude_form_fields = []


class SiteMessagingGroup(ModelViewSetGroup):
    menu_label = "Site Messaging"
    menu_icon = "doc-full-inverse"
    menu_order = 300
    items = (SiteBannerViewSet,)


class GivingGroup(ModelViewSetGroup):
    menu_label = "Giving"
    menu_icon = "link-external"
    menu_order = 290
    items = (DonationPopupViewSet, DonationLinkViewSet, FundraiserViewSet)


@hooks.register("register_admin_viewset")
def register_site_messaging_group():
    return SiteMessagingGroup()


@hooks.register("register_admin_viewset")
def register_giving_group():
    return GivingGroup()


@hooks.register("register_admin_menu_item")
def register_give_today_settings_menu_item():
    # GiveToday is a BaseSiteSetting, not a ModelViewSet, so it can't be a
    # registerable in GivingGroup above (Wagtail's ViewSetRegistry requires every
    # group member to be a real ViewSet with its own on_register/get_urlpatterns).
    # This deep-links straight to its edit page as a top-level item next to Giving,
    # so editors still find it in one place.
    return MenuItem(
        "Give Today (header + book details)",
        reverse("wagtailsettings:edit", args=(GiveToday._meta.app_label, GiveToday._meta.model_name)),
        name="give-today-settings",
        icon_name="cog",
        order=291,
    )
