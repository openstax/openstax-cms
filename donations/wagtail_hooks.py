from django.urls import reverse

from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from global_settings.models import Footer, GiveToday
from global_settings.menu import SettingsLinkMenuItem
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

    def get_submenu_items(self):
        # `items` has to hold real ViewSets, but the submenu is just a list of
        # MenuItems, so the two give-related settings pages belong here too rather
        # than as loose top-level entries beside the group.
        menu_items = super().get_submenu_items()
        settings_links = (
            ("Give Today", GiveToday, "give-today-settings"),
            ("Footer give link", Footer, "footer-give-link-settings"),
        )

        for offset, (label, model, name) in enumerate(settings_links):
            menu_items.append(
                SettingsLinkMenuItem(
                    label, model, name=name, icon_name="cog",
                    order=len(menu_items) + offset + 1
                )
            )
        return menu_items


@hooks.register("register_admin_viewset")
def register_site_messaging_group():
    return SiteMessagingGroup()


@hooks.register("register_admin_viewset")
def register_giving_group():
    return GivingGroup()


@hooks.register("construct_settings_menu")
def remove_give_today_from_settings(request, menu_items):
    # Give Today is reachable from Giving, and it is wholly a giving concern, so a
    # second entry here is just another place for editors to look. Footer stays in
    # Settings: it owns the copyright, AP statement and social links too.
    menu_items[:] = [item for item in menu_items if item.name != "give-today"]
