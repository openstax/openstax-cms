"""Map a Draftail editor's client-side options back to Wagtail feature names.

The rewrite endpoint round-trips content through
``ContentstateConverter(features)``, which silently drops anything outside
``features`` — so converting with a narrower list than the field actually allows
would delete the editor's own markup. The browser knows which plugins its editor
was built with (Wagtail renders them into ``data-w-init-detail-value``) but not
what Wagtail calls them, so the type names are translated back here.
"""

from wagtail.rich_text import features as feature_registry

# Every options key Wagtail's ListFeature subclasses write into (see
# wagtail.admin.rich_text.editors.draftail.features).
_LIST_OPTIONS = ("entityTypes", "blockTypes", "inlineStyles", "decorators", "controls")


def _draftail_feature_index():
    # Forces the register_rich_text_features hooks to run before we read the registry.
    feature_registry.get_default_features()
    plugins = feature_registry.plugins_by_editor.get("draftail", {})

    by_type = {}
    by_flag = {}
    for name, plugin in plugins.items():
        data = getattr(plugin, "data", None)
        if isinstance(data, dict) and "type" in data:
            by_type[data["type"]] = name
        elif getattr(plugin, "option_name", None):
            by_flag[plugin.option_name] = name
    return by_type, by_flag


def features_from_editor_options(options):
    """Return the Wagtail feature names behind a Draftail options dict.

    Falls back to the default feature set when nothing maps, so a payload we
    don't understand degrades to "keep the usual markup" rather than to
    "strip everything".
    """
    by_type, by_flag = _draftail_feature_index()

    names = []
    for key in _LIST_OPTIONS:
        for item in options.get(key) or []:
            if isinstance(item, dict):
                name = by_type.get(item.get("type"))
                if name:
                    names.append(name)

    for flag, name in by_flag.items():
        if options.get(flag):
            names.append(name)

    return names or list(feature_registry.get_default_features())
