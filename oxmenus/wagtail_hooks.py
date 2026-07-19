from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Menus


# SnippetViewSet (not ModelViewSet) so Menus shows up in wagtail-transfer's
# snippet import UI — its model chooser lists SNIPPET_MODELS only. Cross-env
# rows are matched by name via WAGTAILTRANSFER_LOOKUP_FIELDS.
class OXMenusViewSet(SnippetViewSet):
    model = Menus
    icon = "grip"
    menu_label = "OX Menu"
    menu_order = 520
    add_to_admin_menu = True
    list_display = ("name", "sort_order", "key", "feature_flag")
    ordering = ("sort_order", "id")
    search_fields = ("name",)
    exclude_form_fields = []
    # keep the pre-snippet URL layout so /admin/oxmenus/ links survive
    admin_url_namespace = "oxmenus"
    base_url_path = "oxmenus"


register_snippet(OXMenusViewSet)
