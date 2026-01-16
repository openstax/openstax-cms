from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import DonationPopup, Fundraiser


class DonationPopupAdmin(ModelAdmin):
    model = DonationPopup
    menu_icon = 'form'
    menu_label = 'Donation Popup'
    menu_order = 6000
    list_display = ('download_ready', 'header_title', 'hide_donation_popup')
    search_fields = ('header_title', 'header_subtitle', 'download_ready')


class FundraiserAdmin(ModelAdmin):
    model = Fundraiser
    menu_icon = 'site'
    menu_label = 'Fundraisers'
    menu_order = 6100
    list_display = ('headline', 'color_scheme', 'message_type', 'goal_amount', 'goal_time')
    search_fields = ('headline', 'message')


modeladmin_register(DonationPopupAdmin)
modeladmin_register(FundraiserAdmin)
