from django.apps import apps as django_apps


# (target_field_name, base_panel_class_attr, ai_panel_class_attr) tuples.
# Resolved lazily inside apply_ai_panels() so this module imports without wagtail.
_TARGETS = (
    ("title", "TitleFieldPanel", "AITitleFieldPanel"),
    ("search_description", "FieldPanel", "AIDescriptionFieldPanel"),
)


def _build_converters(FieldPanel, TitleFieldPanel, AITitleFieldPanel, AIDescriptionFieldPanel):
    """Return (leaf_converter, string_converter) closures bound to the panel classes.

    A converter maps a panel/field-name we want to AI-enable to its wagtail-ai
    replacement, or returns None when the input is not a target.
    """
    base_for = {"title": TitleFieldPanel, "search_description": FieldPanel}
    ai_for = {"title": AITitleFieldPanel, "search_description": AIDescriptionFieldPanel}
    ai_classes = (AITitleFieldPanel, AIDescriptionFieldPanel)

    def convert_leaf(panel):
        # Already an AI panel -> not a target (keeps this idempotent).
        if isinstance(panel, ai_classes):
            return None
        for field_name, base_cls in base_for.items():
            # Exact type, not isinstance: AI panels subclass these and must not re-match.
            if type(panel) is base_cls and getattr(panel, "field_name", None) == field_name:
                return ai_for[field_name](**panel.clone_kwargs())
        return None

    def convert_string(field_name):
        # Wagtail expands bare field-name strings (e.g. inside a MultiFieldPanel)
        # into FieldPanels at bind time; swap the ones we care about up front.
        if field_name in ai_for:
            return ai_for[field_name](field_name)
        return None

    return convert_leaf, convert_string


def _make_process(PanelPlaceholder, convert_leaf, convert_string):
    """Build the recursive (process_panel, process_list) pair.

    process_panel returns (panel, changed): the (possibly replaced) panel and
    whether anything was swapped at/inside it. We only adopt a constructed
    PanelPlaceholder when a swap actually happened inside it, so placeholders we
    don't care about are left untouched (minimal blast radius).
    """

    def process_list(panels):
        changed = False
        for i, panel in enumerate(panels):
            new_panel, panel_changed = process_panel(panel)
            if panel_changed:
                panels[i] = new_panel
                changed = True
        return changed

    def process_panel(panel):
        if isinstance(panel, str):
            replacement = convert_string(panel)
            return (replacement, True) if replacement is not None else (panel, False)

        leaf = convert_leaf(panel)
        if leaf is not None:
            return leaf, True

        if isinstance(panel, PanelPlaceholder):
            real_panel = panel.construct()
            if real_panel is None:
                return panel, False
            processed, changed = process_panel(real_panel)
            # Only swap the placeholder for its constructed form if we changed
            # something inside; otherwise leave the original placeholder as-is.
            return (processed, True) if changed else (panel, False)

        children = getattr(panel, "children", None)
        if children is not None:
            changed = process_list(children)
            return panel, changed

        return panel, False

    return process_list


def apply_ai_panels():
    """Swap the title and search_description panels of every page type for the
    wagtail-ai equivalents, so the AI suggestion button appears on all pages.

    Handles the three shapes Wagtail 7.x panel definitions take: concrete panel
    instances, PanelPlaceholders (which is how base Page panels ship), bare
    field-name strings nested inside container panels, and models that drive
    their admin through a custom ``edit_handler`` (e.g. books.Book) rather than
    ``content_panels`` / ``promote_panels``.
    """
    from wagtail.admin.panels import FieldPanel, TitleFieldPanel
    from wagtail.models import Page, PanelPlaceholder

    from wagtail_ai.panels import AIDescriptionFieldPanel, AITitleFieldPanel

    convert_leaf, convert_string = _build_converters(
        FieldPanel, TitleFieldPanel, AITitleFieldPanel, AIDescriptionFieldPanel
    )
    process_list = _make_process(PanelPlaceholder, convert_leaf, convert_string)

    for model in django_apps.get_models():
        if not (isinstance(model, type) and issubclass(model, Page)):
            continue
        # Wagtail uses edit_handler when a model defines one, ignoring the
        # content_panels / promote_panels lists; otherwise it builds the editor
        # from those lists. Process whichever the model actually uses.
        if "edit_handler" in model.__dict__:
            process_list(model.edit_handler.children)
        else:
            for attr in ("content_panels", "promote_panels"):
                panels = model.__dict__.get(attr)
                if panels:
                    process_list(panels)
