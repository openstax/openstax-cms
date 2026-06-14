from wagtail.admin.views.generic.models import CreateView, IndexView
from wagtail.admin.views.generic.ordering import ReorderView


class RegionIndexView(IndexView):
    """Index view that lists only menus in a single region."""
    region = None

    def get_base_queryset(self):
        queryset = super().get_base_queryset()
        if self.region:
            queryset = queryset.filter(region=self.region)
        return queryset


class RegionCreateView(CreateView):
    """Create view that pre-selects the region for this section."""
    region = None

    def get_initial_form_instance(self):
        instance = super().get_initial_form_instance() or self.model()
        if self.region:
            instance.region = self.region
        return instance


class RegionReorderView(ReorderView):
    """Reorder view scoped to a single region.

    Without this, drag-and-drop reordering would affect sort_order values
    across ALL regions, corrupting the ordering of items in other regions.
    """
    region = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.region:
            queryset = queryset.filter(region=self.region)
        return queryset
