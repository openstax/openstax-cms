# pages/flex_permissions.py
from rest_framework.permissions import BasePermission


class CanDraftFlexPages(BasePermission):
    """Coarse gate: authenticated staff only. Per-parent add rights are checked
    in the view against Wagtail page permissions."""

    message = "Authenticated CMS staff credentials are required to draft pages."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_staff)
