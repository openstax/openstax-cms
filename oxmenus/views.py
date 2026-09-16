from rest_framework import viewsets
from wagtail.models import Locale

from .models import Menus
from .serializers import OXMenusSerializer


class OXMenusViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OXMenusSerializer

    def get_queryset(self):
        # No `placement` param must keep returning header rows only -- that is
        # the contract the currently-deployed frontend relies on.
        placement = self.request.query_params.get('placement', 'header')
        if placement not in ('header', 'footer'):
            placement = 'header'

        # Menus is translatable, so without this a translated row would be served
        # alongside its source and the nav would render every language at once.
        language_code = self.request.query_params.get('locale')
        locale = (
            Locale.objects.filter(language_code=language_code).first()
            if language_code
            else None
        ) or Locale.get_default()

        return (
            Menus.objects.filter(placement=placement, locale=locale)
            .order_by('sort_order', 'id')
        )
