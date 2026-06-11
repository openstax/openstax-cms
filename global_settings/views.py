from django.contrib.sitemaps import views as sitemap_views
from django.http import HttpResponseServerError, HttpResponse
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from wagtail.models import Page
from global_settings.functions import invalidate_cloudfront_caches


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


def sitemap(request, sitemaps=None, **kwargs):
    if not sitemaps:
        sitemaps = {"wagtail": SlashlessSitemap(request)}
    return sitemap_views.sitemap(request, sitemaps, **kwargs)


# Baseline crawl rules, formerly a static robots.txt served by the frontend.
ROBOTS_STATIC_DISALLOWS = [
    '/accounts',
    '/admin',
    '/l/',
    '/r/',
    '/confirmation/',
    '/adoption-confirmation',
    '/general',
    '/contents',
    '/extras',
    '/errata',
    '/resources',
    '/apps/archive',
    '/apps/archive-preview',
    '/apps/cms/api/spike',
]


def _unpublished_page_paths(request):
    """ Site-relative paths of pages that were published and later unpublished.

        first_published_at filters out never-published drafts: their URLs were
        never live (nothing for a crawler to forget), and listing them in a
        public robots.txt would leak their slugs before launch.
    """
    paths = set()
    unpublished = Page.objects.filter(live=False, first_published_at__isnull=False).specific()
    for page in unpublished:
        url_parts = page.get_url_parts(request=request)
        if url_parts is None:  # page isn't under any Site root
            continue
        page_path = url_parts[2]
        if not page_path:
            continue
        # Match the slash-less canonical URLs the frontend serves (and the
        # sitemap emits); robots.txt rules are prefix matches, so the slash-less
        # form also covers the trailing-slash variant.
        page_path = '/' + page_path.strip('/')
        if page_path == '/':
            continue
        paths.add(page_path)
    return sorted(paths)


def robots(request):
    """ Dynamic robots.txt: static baseline rules plus a Disallow entry for
        every unpublished (previously live) page, so crawlers drop pages that
        editors pull down in the CMS (CORE-2256).
    """
    lines = ['User-agent: *']
    lines += ['Disallow: {}'.format(path) for path in ROBOTS_STATIC_DISALLOWS]
    static_rules = set(ROBOTS_STATIC_DISALLOWS)
    lines += [
        'Disallow: {}'.format(path)
        for path in _unpublished_page_paths(request)
        if path not in static_rules
    ]

    lines += ['', 'User-agent: GPTBot', 'Disallow: /books/']

    root_url = request.build_absolute_uri('/').rstrip('/')
    lines += [
        '',
        'Sitemap: {}/sitemap.xml'.format(root_url),
        'Sitemap: {}/rex/sitemaps/index.xml'.format(root_url),
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')
