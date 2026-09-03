import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from wagtail.admin.auth import require_admin_access

from .rewrite import RewriteError, rewrite_contentstate
from .rewrite_context import build_brief

MAX_LABEL_CHARS = 100


def _page_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@require_admin_access
@require_POST
def rewrite(request):
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "Invalid request."}, status=400)

    contentstate = payload.get("contentstate")
    editor_options = payload.get("editorOptions") or {}
    if (
        not isinstance(contentstate, dict)
        or not isinstance(contentstate.get("blocks"), list)
        or not isinstance(editor_options, dict)
    ):
        return JsonResponse({"error": "Invalid request."}, status=400)

    brief = build_brief(
        page_id=_page_id(payload.get("pageId")),
        field_label=str(payload.get("fieldLabel") or "")[:MAX_LABEL_CHARS],
    )

    try:
        rewritten = rewrite_contentstate(
            contentstate=contentstate,
            editor_options=editor_options,
            brief=brief,
        )
    except RewriteError as error:
        return JsonResponse({"error": str(error)}, status=400)

    return JsonResponse({"contentstate": rewritten})
