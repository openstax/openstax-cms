"""Native Wagtail admin for Salesforce-backed data.

Partners and the related Salesforce data models used to be reachable only through
the Django admin (``/django-admin/...``). That meant editors had to bounce between
two different admin UIs. Here we expose them as native Wagtail ``ModelViewSet``s so
the filters, search, and editing all live inside the Wagtail admin.

Advanced behaviour is gated by *permissions*, not by hiding it behind a second URL:
  * Partner records are pulled from Salesforce, so the Wagtail UI does not allow
    creating them by hand (parity with the old ``has_add_permission = False``).
  * Salesforce-managed fields are shown read-only on the edit form.
  * "Sync Partners with Salesforce" is a header button shown only to users who can
    change partners; it runs the ``update_partners`` management command.

Editing a partner here sets ``from_admin_site`` so the CloudFront-invalidation
``post_save`` signal still fires, exactly as the Django admin did.
"""
from django.core import management
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin import messages
from wagtail.admin.panels import FieldPanel
from wagtail.admin.views.generic.models import CreateView, EditView, IndexView
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup
from wagtail.admin.widgets import HeaderButton

from .models import (
    Partner,
    PartnerTypeMapping,
    PartnerCategoryMapping,
    PartnerFieldNameMapping,
    School,
    AdoptionOpportunityRecord,
    ResourceDownload,
)


# Salesforce owns these fields; editors should see but not change them. Matches
# the ``readonly_fields`` from the old ``PartnerAdmin``.
PARTNER_READONLY_FIELDS = {
    "salesforce_id",
    "account_id",
    "partner_status",
    "partnership_level",
    "equity_rating",
    "partner_sf_account_id",
    "affordability_cost",
    "books",
    "partner_type",
}


def _model_panels(model, readonly_fields=frozenset(), all_readonly=False):
    """Build a panel per concrete field, marking the given fields read-only.

    Built programmatically so new fields appear automatically rather than silently
    dropping off the form (Partner alone has ~90 capability flags)."""
    panels = []
    for field in model._meta.fields:
        if field.auto_created:  # skip the auto PK
            continue
        read_only = all_readonly or field.name in readonly_fields
        panels.append(FieldPanel(field.name, read_only=read_only))
    return panels


# --- Shared mixins ---------------------------------------------------------
class NoAddIndexView(IndexView):
    """Hide the "Add" button for records that are not created by hand."""

    def get_add_url(self):
        return None


class DeniedCreateView(CreateView):
    """Block the add route entirely (parity with has_add_permission = False)."""

    def dispatch(self, request, *args, **kwargs):
        raise PermissionDenied


# --- Partner ---------------------------------------------------------------
class PartnerIndexView(NoAddIndexView):
    @property
    def header_buttons(self):
        buttons = list(super().header_buttons)
        if self.request.user.has_perm("salesforce.change_partner"):
            buttons.append(
                HeaderButton(
                    label=_("Sync with Salesforce"),
                    url=reverse("partners:sync"),
                    icon_name="rotate",
                )
            )
        return buttons


class PartnerEditView(EditView):
    def save_instance(self):
        # Flag the save as coming from the admin so the post_save signal
        # invalidates the CloudFront cache (see salesforce/signals.py).
        self.form.instance.from_admin_site = True
        return super().save_instance()


class PartnerViewSet(ModelViewSet):
    model = Partner
    icon = "group"
    menu_label = "Partners"
    index_view_class = PartnerIndexView
    add_view_class = DeniedCreateView
    edit_view_class = PartnerEditView
    list_display = ("partner_logo_tag", "partner_name", "partner_type", "visible_on_website")
    list_filter = ("visible_on_website", "partner_type")
    search_fields = ("partner_name", "salesforce_id")

    @property
    def panels(self):
        return _model_panels(Partner, readonly_fields=PARTNER_READONLY_FIELDS)

    def sync_view(self, request):
        """Confirm-and-run the Salesforce partner sync (permission gated)."""
        if not request.user.has_perm("salesforce.change_partner"):
            raise PermissionDenied
        index_url = reverse(self.get_url_name("index"))
        if request.method == "POST":
            management.call_command("update_partners", verbosity=0)
            messages.success(request, _("Partners synced with Salesforce."))
            return redirect(index_url)
        from django.template.response import TemplateResponse

        return TemplateResponse(
            request,
            "salesforce/admin/partner_sync.html",
            {"index_url": index_url},
        )

    def get_urlpatterns(self):
        return super().get_urlpatterns() + [
            path("sync/", self.sync_view, name="sync"),
        ]


# --- Partner mapping tables (small config models) --------------------------
class PartnerTypeMappingViewSet(ModelViewSet):
    model = PartnerTypeMapping
    icon = "tag"
    menu_label = "Partner Types"
    list_display = ("display_name",)
    exclude_form_fields = []


class PartnerCategoryMappingViewSet(ModelViewSet):
    model = PartnerCategoryMapping
    icon = "tag"
    menu_label = "Partner Categories"
    list_display = ("display_name", "salesforce_name")
    exclude_form_fields = []


class PartnerFieldNameMappingViewSet(ModelViewSet):
    model = PartnerFieldNameMapping
    icon = "tag"
    menu_label = "Partner Field Names"
    list_display = ("display_name", "salesforce_name")
    exclude_form_fields = []


class PartnersGroup(ModelViewSetGroup):
    menu_label = "Partners"
    menu_icon = "group"
    menu_order = 500
    items = (
        PartnerViewSet("partners"),
        PartnerTypeMappingViewSet("partner_types"),
        PartnerCategoryMappingViewSet("partner_categories"),
        PartnerFieldNameMappingViewSet("partner_field_names"),
    )


# --- Other Salesforce data (read-mostly, synced) ---------------------------
class SchoolViewSet(ModelViewSet):
    model = School
    icon = "home"
    menu_label = "Schools"
    index_view_class = NoAddIndexView
    add_view_class = DeniedCreateView
    list_display = ("name", "salesforce_id", "type", "current_year_students", "total_school_enrollment", "updated")
    list_filter = ("type", "location", "updated")
    search_fields = ("name",)
    exclude_form_fields = []


class AdoptionOpportunityRecordViewSet(ModelViewSet):
    model = AdoptionOpportunityRecord
    icon = "tasks"
    menu_label = "Adoption Opportunities"
    index_view_class = NoAddIndexView
    add_view_class = DeniedCreateView
    list_display = ("account_uuid", "book_name", "students", "savings")
    list_filter = ("book_name", "created", "opportunity_stage")
    search_fields = ("account_uuid", "opportunity_id")

    @property
    def panels(self):
        # These records are synced from Salesforce; show them read-only (parity
        # with the old admin where every field was in readonly_fields).
        return _model_panels(AdoptionOpportunityRecord, all_readonly=True)


class ResourceDownloadViewSet(ModelViewSet):
    model = ResourceDownload
    icon = "download"
    menu_label = "Resource Downloads"
    list_display = ("id", "created", "last_access", "resource_name", "book", "book_format", "account_uuid")
    list_filter = ("created", "book")
    exclude_form_fields = []


class SalesforceDataGroup(ModelViewSetGroup):
    menu_label = "Salesforce Data"
    menu_icon = "table"
    menu_order = 510
    items = (
        SchoolViewSet("schools"),
        AdoptionOpportunityRecordViewSet("adoption_opportunities"),
        ResourceDownloadViewSet("resource_downloads"),
    )


@hooks.register("register_admin_viewset")
def register_partners_group():
    return PartnersGroup()


@hooks.register("register_admin_viewset")
def register_salesforce_data_group():
    return SalesforceDataGroup()
