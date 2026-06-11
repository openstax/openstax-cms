# authoring/views.py
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from wagtail.models import Page

from pages.models import FlexPage
from authoring.permissions import CanDraftFlexPages
from authoring.drafts import create_flex_draft, update_flex_draft, FlexValidationError, PageLockedError
from authoring.routing_rules import validate_page_location, RoutingError


def _review_payload(page, warnings):
    return {
        "id": page.id,
        "slug": page.slug,
        "live": page.live,
        "edit_url": reverse("wagtailadmin_pages:edit", args=[page.id]),
        "preview_url": f"/admin/pages/{page.id}/edit/preview/",
        "warnings": warnings,
    }


class FlexPageDraftView(APIView):
    """Create (POST) or update (PATCH) a FlexPage as an unpublished draft.

    Sets its own auth/permissions so the global AllowAny read posture is untouched.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [CanDraftFlexPages]

    def post(self, request):
        data = request.data
        try:
            parent = Page.objects.get(id=data["parent_id"]).specific
        except (KeyError, Page.DoesNotExist):
            return Response({"errors": {"parent_id": "Unknown or missing parent_id."}},
                            status=status.HTTP_400_BAD_REQUEST)

        # Wagtail per-parent add permission.
        if not parent.permissions_for_user(request.user).can_add_subpage():
            return Response({"errors": {"parent_id": "You cannot add pages here."}},
                            status=status.HTTP_403_FORBIDDEN)

        # Routing rules enforce reserved slugs, RootPage-only parents, and
        # tree-global slug uniqueness (suffixing + warning on collision).
        try:
            slug, routing_warnings = validate_page_location(parent, data.get("slug", ""))
        except RoutingError:
            return Response(
                {"errors": {"slug": "Invalid page location or slug."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            page, _ = create_flex_draft(
                parent=parent, title=data.get("title", ""), slug=slug,
                layout_data=data.get("layout"), body_data=data.get("body", []),
                user=request.user,
            )
        except FlexValidationError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_review_payload(page, routing_warnings),
                        status=status.HTTP_201_CREATED)

    def patch(self, request, page_id):
        try:
            page = FlexPage.objects.get(id=page_id)
        except FlexPage.DoesNotExist:
            return Response({"errors": {"page_id": "Unknown FlexPage."}},
                            status=status.HTTP_404_NOT_FOUND)
        if not page.permissions_for_user(request.user).can_edit():
            return Response({"errors": {"page_id": "You cannot edit this page."}},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            page, _ = update_flex_draft(
                page=page, title=request.data.get("title"),
                layout_data=request.data.get("layout"), body_data=request.data.get("body"),
                user=request.user,
            )
        except FlexValidationError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        except PageLockedError:
            return Response(
                {"errors": {"page_id": "This page is locked and cannot be edited right now."}},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(_review_payload(page, []), status=status.HTTP_200_OK)
