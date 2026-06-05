from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from .models import DonationPopup, Fundraiser, SiteBanner
from global_settings.models import GiveToday


class DonationPopupAdmin(ModelAdmin):
    model = DonationPopup
    menu_icon = 'form'
    menu_label = 'Donation Popup'
    list_display = ('download_ready', 'header_title', 'hide_donation_popup')
    search_fields = ('header_title', 'header_subtitle', 'download_ready',)


class FundraiserAdmin(ModelAdmin):
    model = Fundraiser
    menu_icon = 'site'
    menu_label = 'Fundraisers'
    list_display = ('headline', 'color_scheme', 'message_type', 'goal_amount', 'goal_time')
    search_fields = ('headline', 'message',)


class GiveTodayAdmin(ModelAdmin):
    model = GiveToday
    menu_icon = 'date'
    menu_label = 'Give Today'
    list_display = ('give_link_text', 'start', 'expires')
    search_fields = ('give_link_text',)


class SiteBannerAdmin(ModelAdmin):
    model = SiteBanner
    menu_icon = 'doc-full-inverse'
    menu_label = 'Site Banners'
    list_display = ('name', 'is_active', 'start_date', 'end_date', 'context_filter')
    search_fields = ('name', 'html_message',)
    list_filter = ('is_active', 'context_filter',)


class SiteMessagingModalsGroup(ModelAdminGroup):
    menu_label = 'Site Messaging'
    menu_icon = 'doc-full-inverse'
    menu_order = 600
    items = (DonationPopupAdmin, FundraiserAdmin, GiveTodayAdmin, SiteBannerAdmin,)


modeladmin_register(SiteMessagingModalsGroup)
