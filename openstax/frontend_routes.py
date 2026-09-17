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

# The subset of the above that FlexPage.get_url_parts has to reflect, keyed the
# other way round (slug -> osweb route).
#
# Resolving a mismatched URL is only half the job. Where the match is a
# FlexPage, the crawler is served the page's own full template, whose canonical,
# og:url and sitemap <loc> all come from get_url_parts -- so without this the
# snapshot at /press would declare /news canonical, and /news 301s to /blog.
#
# The other two slugs in SLUG_MISMATCHES are left out for their own reasons,
# not by oversight:
#
#   'supporters' -- /supporters is the canonical URL for that FlexPage and
#     serves it directly, so get_url_parts already reports the right thing.
#     Only the stale /foundation alias redirects in.
#   'institutional-partnership' -- that page is a pages.InstitutionalPartnership
#     rather than a FlexPage, so this map cannot reach it. The crawler gets the
#     meta-only snapshot instead of the page's own template, and that
#     snapshot's canonical is built from the requested URL
#     (/institutional-partnership-application), never from get_url_parts.
FLEXPAGE_ROUTES_BY_SLUG = {
    'news': 'press',
}

# Routes whose copy lives on the single FormHeadings record instead of on a page
# of their own, in fields named ``<route>_intro_heading`` and
# ``<route>_intro_description``. Keeping the copy there means marketing edits
# what crawlers see in Wagtail, with no redeploy and no duplicate page.
FORM_PAGE_ROUTES = ('adoption', 'interest')

# Routes with no CMS record at all, mapped to (title, description). This is the
# only hardcoded SEO copy here; everything else is editable in Wagtail. The
# title mirrors the <h1> in os-webview src/app/pages/adopters/adopters.tsx.
#
# These snapshots deliberately carry no body. /adopters renders 11,000+
# institutions from /apps/cms/api/adopters/, and that payload's ``description``
# field is unpublished CRM free text which the page itself never displays.
# Serving it to crawlers alone would leak internal notes and be cloaking.
STATIC_PAGES = {
    'adopters': (
        'Complete list of institutions that have adopted OpenStax',
        'Institutions around the world that have adopted OpenStax free, '
        'openly licensed textbooks.',
    ),
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


def sitemap_routes():
    """ Routes sitemap.xml has to advertise itself, because no Wagtail page's
        get_sitemap_urls() covers them.

        Routes in SLUG_MISMATCHES are excluded: the CMS page they resolve to is
        already in the Wagtail-generated section. Form routes appear only while
        their copy exists, since that is exactly when the middleware can answer
        them.
    """
    headings = form_headings()
    return tuple(
        route for route in FORM_PAGE_ROUTES if form_route_heading(headings, route)
    ) + tuple(STATIC_PAGES)
