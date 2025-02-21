from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import redirect
from django.urls import reverse, path
from django.conf import settings

from rest_framework.response import Response

from wagtail.models import Page, PageViewRestriction, Site
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
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
            instance = self.get_object()

            if request.GET.get('draft'):
                instance = instance.get_latest_revision_as_object()

            serializer = self.get_serializer(instance)
            return Response(serializer.data)
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

    def get_base_queryset(self):
        """
        this method copied from https://github.com/wagtail/wagtail/blob/main/wagtail/api/v2/views.py#L491
        so that we can change the line that says:
             queryset = Page.objects.all().live()
        to:
             queryset = Page.objects.all()

        when viewing draft content is enabled
        """

        request = self.request

        if request.GET.get('draft'):
            # Get all pages including drafts
            queryset = Page.objects.all()
        else:
            # Get all live pages
            queryset = Page.objects.all().live()

        # Exclude pages that the user doesn't have access to
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.select_related("page")
            if not restriction.accept_request(self.request)
        ]

        # Exclude the restricted pages and their descendants from the queryset
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)

        # Check if we have a specific site to look for
        if "site" in request.GET:
            # Optionally allow querying by port
            if ":" in request.GET["site"]:
                (hostname, port) = request.GET["site"].split(":", 1)
                query = {
                    "hostname": hostname,
                    "port": port,
                }
            else:
                query = {
                    "hostname": request.GET["site"],
                }
            try:
                site = Site.objects.get(**query)
            except Site.MultipleObjectsReturned:
                raise BadRequestError(
                    "Your query returned multiple sites. Try adding a port number to your site filter."
                )
        else:
            # Otherwise, find the site from the request
            site = Site.find_for_request(self.request)

        if site:
            base_queryset = queryset
            queryset = base_queryset.descendant_of(site.root_page, inclusive=True)

            # If internationalisation is enabled, include pages from other language trees
            if getattr(settings, "WAGTAIL_I18N_ENABLED", False):
                for translation in site.root_page.get_translations():
                    queryset |= base_queryset.descendant_of(translation, inclusive=True)

        else:
            # No sites configured
            queryset = queryset.none()

        return queryset


class OpenStaxImagesAPIViewSet(ImagesAPIViewSet):
    meta_fields = BaseAPIViewSet.meta_fields + ['tags', 'download_url', 'height', 'width']
    nested_default_fields = BaseAPIViewSet.nested_default_fields + ['title', 'download_url', 'height', 'width']

# Create the router. “wagtailapi” is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', OpenstaxPagesAPIEndpoint)
api_router.register_endpoint('images', OpenStaxImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)
