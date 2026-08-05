from wagtail.admin.forms.models import formfield_for_dbfield
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Without panels/edit_handler, bare ModelViewSet.get_edit_handler()
        # returns None and get_form_class() falls back to a plain
        # modelform_factory whose default formfield_for_dbfield skips
        # Wagtail's admin widget registry -- so start/end silently lost the
        # AdminDateTimeInput calendar picker (and its initDateTimeChooser JS)
        # in favor of a bare text input. Delegate to Wagtail's own
        # registry-aware version instead of Django's default.
        return formfield_for_dbfield(db_field, **kwargs)
