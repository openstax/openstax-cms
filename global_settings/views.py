from django.contrib.sitemaps import Sitemap as StaticSitemap
from django.contrib.sitemaps import views as sitemap_views
from django.http import HttpResponseServerError, HttpResponse
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from global_settings.functions import invalidate_cloudfront_caches
from openstax.frontend_routes import FORM_PAGE_ROUTES, form_headings, sitemap_routes


def throw_error(request):
        # Return an "Internal Server Error" 500 response code.
        return HttpResponseServerError()


def clear_entire_cache(request):
        # clear all contents from the Cloudfront cache
        invalidate_cloudfront_caches()
        response = '<html><body><p>All Caches Invalidated</p></body></html>'
        return HttpResponse(response)


class SlashlessSitemap(Sitemap):
    """ Wagtail sitemap that emits canonical, slash-less <loc> URLs.

        WAGTAIL_APPEND_SLASH=True makes ordinary pages render with a trailing
        slash, while several models (blog, press, general pages) hard-code
        slash-less paths in get_url_parts(). That produced a sitemap mixing
        /foo/ and /foo entries. Stripping the trailing slash here keeps every
        <loc> consistent and matches the slash-less canonical URLs the frontend
        serves.

        Wagtail's Sitemap._urls() builds each <loc> from the page's
        get_sitemap_urls()/get_full_url() and never calls location(), so the
        trailing slash is stripped from the generated url_info entries here.
    """
    def _urls(self, page, protocol, domain):
        urls = super()._urls(page, protocol, domain)
        for url_info in urls:
            location = url_info.get('location')
            if location is not None:
                url_info['location'] = location.rstrip('/')
        return urls


class FrontendOnlyPagesSitemap(StaticSitemap):
    """ Routes osweb serves from the SPA with no Wagtail page of their own.

        SlashlessSitemap walks the page tree, so it cannot see these -- which is
        why /adoption was absent from sitemap.xml entirely and Google had no way
        to discover it. Sourced from the same registry the OG middleware
        resolves, so a route cannot be advertised here while still 404ing to
        crawlers (the failure /blog is in today).

        <loc>s are slash-less to match SlashlessSitemap and the canonical URLs
        the frontend serves.
    """
    protocol = 'https'
    changefreq = 'monthly'

    def items(self):
        # sitemap_routes() is evaluated per request, not at import: the form
        # routes it returns depend on CMS content, and a route the middleware
        # can't answer must not be advertised here. The record is held for
        # lastmod() below, so this is one query rather than one per route.
        self.headings = form_headings()
        return list(sitemap_routes(self.headings))

    def location(self, route):
        return '/{}'.format(route)

    def lastmod(self, route):
        """ When the copy behind `route` last changed.

            Only the form routes have a CMS record to date. STATIC_PAGES copy
            lives in this repo, so there is nothing truthful to report for it
            and it gets no <lastmod> rather than an invented one.
        """
        if route in FORM_PAGE_ROUTES:
            return getattr(self.headings, 'last_published_at', None)
        return None

    def _urls(self, page, protocol, domain):
        urls = super()._urls(page, protocol, domain)
        # Django sets latest_lastmod only when *every* item has a lastmod, and
        # views.sitemap drops the response's Last-Modified header unless every
        # section reports one. So an undated /adopters here would have taken
        # that header off the whole document, including the Wagtail section
        # that supplies it today. Report the newest date this section knows.
        if getattr(self, 'latest_lastmod', None) is None:
            known = [url['lastmod'] for url in urls if url.get('lastmod')]
            if known:
                self.latest_lastmod = max(known)
        return urls


def sitemap(request, sitemaps=None, **kwargs):
    """ Both sections in one document.

        django.contrib.sitemaps.views.sitemap concatenates every section's URLs
        into a single <urlset>; it is views.index that emits a sitemap index and
        reverses a per-section URL name. Only the former is routed
        (openstax/urls.py), so there are no sitemap-<section>.xml URLs to wire
        up and adding a section needs no URLconf change.
    """
    if not sitemaps:
        sitemaps = {
            "wagtail": SlashlessSitemap(request),
            "frontend-only": FrontendOnlyPagesSitemap(),
        }
    response = sitemap_views.sitemap(request, sitemaps, **kwargs)
    # The frontend-only section is derived from CMS state at request time, so a
    # cached copy can advertise /adoption after the middleware has stopped
    # serving it -- the inconsistency this section exists to prevent, just
    # moved to the edge. CloudFront doesn't cache this path today (every
    # request is a Miss, no Cache-Control, no Age), but that is CDN
    # configuration rather than anything this repo controls, and page-publish
    # invalidation only covers /apps/cms/api/* (global_settings.functions).
    # Saying it in the response keeps the invariant independent of both.
    response.headers['Cache-Control'] = 'no-cache'
    return response
