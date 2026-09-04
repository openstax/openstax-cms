"""Rewrite a fragment of Draftail content in the OpenStax voice.

The browser sends ContentState, not HTML: Wagtail's own converter turns it into
the database HTML, and back again afterwards. That reuses the field's real
feature list in both directions, so whatever the model invents that the field
does not allow is dropped on the way in rather than sanitised by hand.
"""

import json
import logging
import re

from wagtail.admin.rich_text.converters.contentstate import ContentstateConverter
from wagtail.rich_text import features as feature_registry
from wagtail_ai.agents.base import get_llm_service

from .prompts import voice_prompt
from .draftail_features import features_from_editor_options

logger = logging.getLogger(__name__)

PROVIDER_ALIAS = "default"
MAX_HTML_CHARS = 12000

_FENCE = re.compile(r"\A```[a-z]*\s*|\s*```\Z", re.IGNORECASE)


class RewriteError(Exception):
    """Something went wrong that the editor should be told about."""


def allowed_tags(features):
    tags = set()
    for feature in features:
        rule = feature_registry.get_converter_rule("contentstate", feature) or {}
        for selector in rule.get("from_database_format", {}):
            tags.add(selector.split("[")[0])
    return ", ".join(f"<{tag}>" for tag in sorted(tags)) or "<p>"


def _completion(instruction, html):
    service = get_llm_service(alias=PROVIDER_ALIAS)
    result = service.completion(
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": html},
        ]
    )
    return result.choices[0].message.content


def rewrite_contentstate(*, contentstate, editor_options, brief):
    """Return the rewritten ContentState for one fragment of a rich text field."""
    features = features_from_editor_options(editor_options)
    converter = ContentstateConverter(features)

    if not any(block.get("text", "").strip() for block in contentstate["blocks"]):
        raise RewriteError("There's no text here to rewrite.")

    html = converter.to_database_format(json.dumps(contentstate))
    if len(html) > MAX_HTML_CHARS:
        raise RewriteError("That's too much text at once — select less of it.")

    try:
        reply = _completion(voice_prompt(brief, allowed_tags(features)), html)
    except Exception as error:
        logger.exception("OpenStax voice rewrite failed")
        raise RewriteError("The rewrite service didn't answer. Try again.") from error

    reply = _FENCE.sub("", (reply or "").strip())
    if not reply:
        raise RewriteError("The rewrite came back empty. Try again.")

    rewritten = json.loads(converter.from_database_format(reply))
    if not any(block.get("text", "").strip() for block in rewritten.get("blocks", [])):
        # Everything the model sent was outside the field's feature list.
        raise RewriteError("The rewrite didn't fit this field. Try again.")
    return rewritten
