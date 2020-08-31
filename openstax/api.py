from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import redirect
from django.urls import reverse, path

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet



class OpenstaxPagesAPIEndpoint(PagesAPIViewSet):
    """
    OpenStax custom Pages API endpoint that allows finding pages and books by pk or slug
    """

    def detail_view(self, request, pk=None, slug=None):
        param = pk
        if slug is not None:
            self.lookup_field = 'slug'
            param = slug
        try:
            return super().detail_view(request, param)
        except MultipleObjectsReturned:
            # Redirect to the listing view, filtered by the relevant slug
            # The router is registered with the `wagtailapi` namespace,
            # `pages` is our endpoint namespace and `listing` is the listing view url name.
            return redirect(
                reverse('wagtailapi:pages:listing') + f'?{self.lookup_field}={param}'
            )

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path('', cls.as_view({'get': 'listing_view'}), name='listing'),
            path('<int:pk>/', cls.as_view({'get': 'detail_view'}), name='detail'),
            path('<slug:slug>/', cls.as_view({'get': 'detail_view'}), name='detail'),
            path('find/', cls.as_view({'get': 'find_view'}), name='find'),
        ]

# Create the router. “wagtailapi” is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', OpenstaxPagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)