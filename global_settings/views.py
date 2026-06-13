from django.contrib.sitemaps import views as sitemap_views
from django.http import HttpResponseServerError, HttpResponse
from django.shortcuts import render
from wagtail.admin.auth import require_admin_access
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from global_settings.functions import invalidate_cloudfront_caches


@require_admin_access
def experiments_guide(request):
    return render(request, 'experiments_guide.html', {
        'posthog_project_url': 'https://us.posthog.com/project/105101',
        'framework_doc': 'https://github.com/openstax/openstax-cms/blob/main/docs/posthog-experiments-measurement.md',
        'runbook_doc': 'https://github.com/openstax/openstax-cms/blob/main/docs/posthog-experiments-runbook.md',
    })


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
