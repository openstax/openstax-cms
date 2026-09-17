""" Facts about the routes osweb serves from the SPA rather than from a Wagtail
    page of its own.

    openstax.org serves crawler user-agents from this CMS instead of the
    S3-hosted osweb bundle -- nginx switches on User-Agent -- so anything osweb
    routes client-side has to resolve here too. When it doesn't, the crawler
    gets a 404 for a URL that works perfectly well in a browser, which is what
    kept /adoption out of Google's index (CORE-736).

    Everything here mirrors os-webview
    src/app/components/shell/router-helpers/page-routes.tsx: SLUG_MISMATCHES is
    its ``mismatch`` map, and the rest are entries from its ``isNoDataPage()``
    list. Nothing links the two repos at build time, so they are kept in sync
    by hand -- adding an SPA-only route there means adding it here.
"""

# Top-level osweb URLs whose content lives on a CMS page under a different
# slug. osweb keeps the same mapping in its ``mismatch`` map.
#
# 'foundation' may be redundant: bit-deployment's nginx uri-map 301s /foundation
# to /supporters before Django ever sees it. Kept because the middleware is also
# reachable in environments that don't sit behind that nginx config.
SLUG_MISMATCHES = {
    'foundation': 'supporters',
    'press': 'news',
    'institutional-partnership-application': 'institutional-partnership',
}

# The subset of the above that the page models' get_url_parts has to reflect,
# keyed the other way round (slug -> osweb route).
#
# Resolving a mismatched URL is only half the job. get_url_parts feeds the
# sitemap <loc>, the API's html_url, and -- where the crawler is served the
# page's own template -- its canonical and og:url. A page whose slug is
# mismatched therefore has to report the URL osweb serves it at, or the sitemap
# advertises a URL that redirects away while the one that works goes
# unadvertised. Both entries here were live instances of that:
#
#   'news' -- listed as /news, which 301s to /blog, while /press was absent.
#   'institutional-partnership' -- listed as /institutional-partnership, which
#     301s to /higher-education, while /institutional-partnership-application
#     (200 in a browser) was absent.
#
# 'supporters' is deliberately not here: /supporters is the canonical URL for
# that page and serves it directly, so get_url_parts already reports the right
# thing. Only the stale /foundation alias redirects in.
PAGE_ROUTES_BY_SLUG = {
    'news': 'press',
    'institutional-partnership': 'institutional-partnership-application',
}

# Routes whose copy lives on the single FormHeadings record instead of on a page
# of their own, in fields named ``<route>_intro_heading`` and
# ``<route>_intro_description``. Keeping the copy there means marketing edits
# what crawlers see in Wagtail, with no redeploy and no duplicate page.
FORM_PAGE_ROUTES = ('adoption', 'interest')

# Routes with no CMS record at all. This is the only hardcoded SEO copy here;
# everything else is editable in Wagtail, so each entry takes its wording from
# whatever the osweb page itself already declares rather than inventing any.
STATIC_PAGES = {
    # Title is the <h1> in os-webview src/app/pages/adopters/adopters.tsx,
    # which is all that page declares.
    #
    # No body, on purpose: /adopters renders 11,000+ institutions from
    # /apps/cms/api/adopters/, and that payload's ``description`` field is
    # unpublished CRM free text which the page itself never displays. Serving
    # it to crawlers alone would leak internal notes and be cloaking.
    'adopters': {
        'title': 'Complete list of institutions that have adopted OpenStax',
        'description': 'Institutions around the world that have adopted '
                       'OpenStax free, openly licensed textbooks.',
    },
    # Title and description are the ones separatemap.tsx passes to
    # useDocumentHead() -- the page does describe itself, just in JavaScript,
    # where a crawler never sees it. Serving the same strings keeps the
    # crawler's title identical to the browser's.
    #
    # The body is the sentence that introduces this map on /about ("Our global
    # reach"), because the page itself is an interactive map with no prose to
    # read. Published copy, not written for crawlers.
    'separatemap': {
        'title': 'Institution Map - OpenStax',
        'description': 'Searchable map of institutions that have adopted '
                       'OpenStax textbooks',
        'body': '<p>OpenStax is used in classrooms across the U.S. and more '
                'than 160 countries. Find your school on the map.</p>',
    },
}


def form_headings():
    """ The published FormHeadings record the form routes read their copy from.

        max_count = 1 is per-locale (there is an en record and an es one), so
        this pins the default locale rather than assuming a single row. Returns
        None when there is no such record, e.g. on a fresh database.

        live() and public() are what keep unreleased copy out of a crawler's
        hands: the middleware renders this straight into a snapshot, so a record
        an editor has only drafted (or has unpublished, or has put behind a view
        restriction) would otherwise be published to Google by this path alone.
        Skipping it here also drops the route from sitemap_routes(), since both
        go through form_route_heading() below.

        Imported inside the function because this module is imported from
        pages.models, so importing the models here would be circular.
    """
    from pages.models import FormHeadings
    from wagtail.models import Locale

    return FormHeadings.objects.live().public().filter(
        locale=Locale.get_default()
    ).first()


def form_route_heading(headings, route):
    """ The heading `route` builds its crawler snapshot around, or '' if the
        FormHeadings record has no copy for it.

        Always the logged-out field: a crawler is never signed in, and the
        logged-in variants are the ones carrying {{first_name}} tags.

        This is the one place that decides whether a form route can be served,
        so the middleware and sitemap_routes() below agree by construction -- a
        route with nothing to render must not be advertised, which is the bug
        (advertised in sitemap.xml, 404 to crawlers) this module exists to make
        unrepresentable.
    """
    if headings is None:
        return ''
    return (getattr(headings, '{}_intro_heading'.format(route), '') or '').strip()


# Distinguishes "no record supplied" from "supplied, and there isn't one".
_UNSET = object()


def sitemap_routes(headings=_UNSET):
    """ Routes sitemap.xml has to advertise itself, because no Wagtail page's
        get_sitemap_urls() covers them.

        Routes in SLUG_MISMATCHES are excluded: the CMS page they resolve to is
        already in the Wagtail-generated section. Form routes appear only while
        their copy exists, since that is exactly when the middleware can answer
        them.

        Pass `headings` to reuse a record the caller has already fetched -- the
        sitemap needs it again for each route's <lastmod>.
    """
    if headings is _UNSET:
        headings = form_headings()
    return tuple(
        route for route in FORM_PAGE_ROUTES if form_route_heading(headings, route)
    ) + tuple(STATIC_PAGES)
