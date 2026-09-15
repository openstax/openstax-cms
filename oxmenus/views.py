from rest_framework import viewsets
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
        return Menus.objects.filter(placement=placement).order_by('sort_order', 'id')
