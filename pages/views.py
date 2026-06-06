from django.http import HttpResponse
from django.views.generic import TemplateView

from wagtail.admin.userbar import Userbar


class HeadlessUserbarView(TemplateView):
    """Render Wagtail's userbar for the decoupled (headless) front-end.

    While previewing a draft, the front-end fetches this endpoint, injects the
    returned markup, and loads Wagtail's ``vendor.js``/``userbar.js``. Loading
    the userbar is what enables live-preview scroll restoration, the
    accessibility/content checker, content metrics, and wagtail-ai's content
    checks on the decoupled front-end (per the Wagtail headless docs). The
    front-end and CMS share an origin, so no CORS headers are needed.
    """

    http_method_names = ["get"]
    template_name = Userbar.template_name

    def get(self, request, *args, **kwargs):
        # Mirror the {% wagtailuserbar %} gate: never expose editor tooling or
        # edit links to anyone without admin access.
        if not request.user.has_perm("wagtailadmin.access_admin"):
            return HttpResponse("")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return Userbar(object=None, position="bottom-right").get_context_data(
            super().get_context_data(request=self.request, **kwargs)
        )
