""" Facts about the routes osweb serves from the SPA rather than from a Wagtail
    page of its own.

    openstax.org serves crawler user-agents from this CMS instead of the
    S3-hosted osweb bundle -- nginx switches on User-Agent -- so anything osweb
    routes client-side has to resolve here too. When it doesn't, the crawler
    gets a 404 for a URL that works perfectly well in a browser, which is what
    kept /adoption out of Google's index (CORE-736).

    Everything here comes from os-webview
    src/app/components/shell/router-helpers/page-routes.tsx and the page
    components it routes to. Nothing links the two repos at build time, so they
    are kept in sync by hand -- adding an SPA-only route there means adding it
    here. Checked against that file rather than inferred: reading it is what
    turned up the /edtech-partner-program entry below, which was 200 in a
    browser and 404 to crawlers.
"""

# Top-level osweb URLs whose content lives on a CMS page under a different
# slug. The first three are osweb's ``mismatch`` map verbatim.
#
# 'institutional-partnership-application' is not in that map -- it is an
# ``isNoDataPage()`` route, but its page component
# (pages/institutional-partnership-application) renders
# <LoaderPage slug="pages/institutional-partnership" doDocumentSetup>, so the
# CMS page is still where its content and its document head come from.
#
# 'foundation' may be redundant: bit-deployment's nginx uri-map 301s /foundation
# to /supporters before Django ever sees it. Kept because the middleware is also
# reachable in environments that don't sit behind that nginx config.
SLUG_MISMATCHES = {
    'foundation': 'supporters',
    'press': 'news',
    'edtech-partner-program': 'openstax-ally-technology-partner-program',
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
# The other two mismatched slugs are deliberately not here:
#
#   'supporters' -- /supporters is the canonical URL for that page and serves
#     it directly, so get_url_parts already reports the right thing. Only the
#     stale /foundation alias redirects in.
#   'openstax-ally-technology-partner-program' -- unlike the two above, that
#     URL doesn't redirect anywhere; it serves the page, and GeneralPage keeps
#     it out of the sitemap regardless (get_sitemap_urls returns [] for every
#     slug but three). So nothing here is broken, and which of its two working
#     URLs should be canonical is a content decision rather than a defect --
#     see the PR discussion.
PAGE_ROUTES_BY_SLUG = {
    'news': 'press',
    'institutional-partnership': 'institutional-partnership-application',
}
