from django.urls import path, reverse
from django.utils.html import format_html, json_script
from wagtail import hooks
from wagtail.admin.staticfiles import versioned_static

from .views import rewrite


@hooks.register("register_admin_urls")
def register_ai_assist_urls():
    return [path("ai-assist/rewrite/", rewrite, name="ai_assist_rewrite")]


@hooks.register("insert_global_admin_js")
def ai_assist_draftail_js():
    config = {"rewriteUrl": reverse("ai_assist_rewrite")}
    return format_html(
        '{}<script src="{}"></script>',
        json_script(config, "ai-assist-config"),
        versioned_static("ai_assist/draftail_rewrite.js"),
    )
