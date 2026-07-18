from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from wagtail.models import Page, Site

from pages.models import FlexPage
from pages.promote_home import PromoteError, promote_to_home

# register_admin_urls wraps every URL from this hook in require_admin_access
# (wagtail/admin/urls/__init__.py), so anonymous/non-staff users are already
# redirected to admin login before this view runs.


def _current_home_page():
    """Best-effort lookup of the home page, for display only (not the
    permission/lock gate — promote_to_home is authoritative for that)."""
    site = Site.objects.filter(is_default_site=True).first()
    return site.root_page.specific if site else None


def promote_to_home_view(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    if type(page.specific) is not FlexPage:
        raise Http404("Not a FlexPage.")
    flex_page = page.specific

    if request.method == 'POST':
        try:
            revision = promote_to_home(flex_page, request.user)
        except PromoteError as exc:
            messages.error(request, str(exc))
            return redirect('promote_to_home', page_id=page_id)

        messages.success(
            request,
            "Home page draft updated from '{}'. Review and publish it.".format(flex_page.title),
        )
        return redirect('wagtailadmin_pages:edit', revision.object_id)

    return render(request, 'pages/promote_to_home_confirm.html', {
        'flex_page': flex_page,
        'home_page': _current_home_page(),
        'page_title': "Promote to home page",
    })
