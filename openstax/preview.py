from django.http import HttpResponseRedirect


class FrontendPreviewMixin:
    """Redirect the Wagtail preview panel to the headless frontend.

    This CMS is headless: the Django ``page.html`` template is only a raw
    fallback, and the real page is rendered by the frontend SPA. Without this
    mixin, Wagtail's default ``serve_preview`` renders ``page.html`` instead of
    the actual site, so every previewed page looks like unstyled content.

    Mix this in *before* ``wagtail.models.Page`` on any page type that has a
    frontend route. It relies on the page's ``get_url_parts`` to produce the
    correct frontend-relative URL, so a page only needs to keep returning the
    right path there (as the models already do).

    Per the Wagtail 7.1+ recommendation against nested preview iframes, the
    preview panel is redirected straight to the frontend (same origin) so
    Wagtail's content checks read the rendered page directly.
    """

    def serve_preview(self, request, mode_name):
        url_parts = self.get_url_parts(request)
        # get_url_parts returns None when no Site resolves to this page (e.g. a
        # freshly-created page tree before the Site is wired up); fall back to
        # Wagtail's default preview rather than crashing on the unpack.
        if url_parts is None:
            return super().serve_preview(request, mode_name)
        site_id, site_root, relative_page_url = url_parts
        # Use a root-relative URL (drop site_root) so the preview inherits the
        # admin's scheme/origin. site_root carries the scheme baked into the
        # Site record's port (http:// for the conventional port-80 config),
        # which the browser blocks as mixed content under the HTTPS admin. This
        # matches the path-relative URL convention in openstax/functions.py.
        preview_url = '{}/?preview={}'.format(relative_page_url, mode_name)
        return HttpResponseRedirect(preview_url)
