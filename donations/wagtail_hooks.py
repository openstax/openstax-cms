from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from .models import DonationPopup, Fundraiser, SiteBanner


class DonationPopupViewSet(ModelViewSet):
    model = DonationPopup
    icon = "form"
    menu_label = "Donation Popup"
    list_display = ("download_ready", "header_title", "hide_donation_popup")
    search_fields = ("header_title", "header_subtitle", "download_ready")
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
    items = (DonationPopupViewSet, FundraiserViewSet, SiteBannerViewSet)


@hooks.register("register_admin_viewset")
def register_site_messaging_group():
    return SiteMessagingGroup()
