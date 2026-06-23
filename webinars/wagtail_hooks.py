from wagtail.admin.viewsets.model import ModelViewSet

from .models import Webinar


class WebinarViewSet(ModelViewSet):
    name = "webinars"
    model = Webinar
    icon = "media"
    menu_label = "Webinars"
    menu_order = 230
    add_to_admin_menu = False
    list_display = ("title", "start", "end", "spaces_remaining")
    list_filter = ("start", "display_on_tutor_page")
    search_fields = ("title",)
    exclude_form_fields = []
