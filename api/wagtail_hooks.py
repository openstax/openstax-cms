from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import FeatureFlag


class FeatureFlagViewSet(SnippetViewSet):
    model = FeatureFlag
    icon = "cog"
    menu_label = "Feature Flags"
    add_to_settings_menu = True
    list_display = ("name", "feature_active", "description", "updated")
    list_filter = ("feature_active",)
    search_fields = ("name", "description")


register_snippet(FeatureFlagViewSet)
