from django.urls import reverse

from wagtail.admin.menu import MenuItem


class SettingsLinkMenuItem(MenuItem):
    """Deep-links a BaseSiteSetting from elsewhere in the admin menu.

    Wagtail's own SettingMenuItem does the same permission check but derives its
    label from the model's verbose_name, and these items need labels that say where
    they sit ("Footer Content" under the Footer group, for instance). A plain
    MenuItem would show to everyone and 403 on click.
    """

    def __init__(self, label, model, **kwargs):
        self.permission_policy = model.get_permission_policy()
        super().__init__(
            label,
            reverse("wagtailsettings:edit", args=(model._meta.app_label, model._meta.model_name)),
            **kwargs,
        )

    def is_shown(self, request):
        return self.permission_policy.user_has_permission(request.user, "change")
