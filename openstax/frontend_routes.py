""" Facts about the routes osweb serves under a URL that isn't its CMS slug.

    openstax.org serves crawler user-agents from this CMS instead of the
    S3-hosted osweb bundle -- nginx switches on User-Agent -- so the URLs this
    CMS reports have to be the ones osweb actually serves (CORE-736).

    Everything here comes from os-webview
    src/app/components/shell/router-helpers/page-routes.tsx and the page
    components it routes to. Nothing links the two repos at build time, so they
    are kept in sync by hand.
"""

# Pages whose get_url_parts has to reflect the URL osweb serves them at,
# keyed slug -> osweb route.
#
# get_url_parts feeds the sitemap <loc>, the API's html_url, and -- where the
# crawler is served the page's own template -- its canonical and og:url. A page
# whose slug differs from its osweb route therefore has to report the route, or
# the sitemap advertises a URL that redirects away while the one that works
# goes unadvertised. Both entries here were live instances of that:
#
#   'news' -- listed as /news, which 301s to /blog, while /press was absent.
#   'institutional-partnership' -- listed as /institutional-partnership, which
#     301s to /higher-education, while /institutional-partnership-application
#     (200 in a browser) was absent.
PAGE_ROUTES_BY_SLUG = {
    'news': 'press',
    'institutional-partnership': 'institutional-partnership-application',
}
