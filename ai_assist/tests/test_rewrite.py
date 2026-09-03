import json
from types import SimpleNamespace
from unittest import mock

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse
from wagtail.admin.rich_text import DraftailRichTextArea
from wagtail.admin.rich_text.converters.contentstate import ContentstateConverter
from wagtail.models import Page
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailTestUtils

from ai_assist.draftail_features import features_from_editor_options
from ai_assist.rewrite import MAX_HTML_CHARS, RewriteError, allowed_tags, rewrite_contentstate
from ai_assist.rewrite_context import build_brief
from pages.models import GeneralPage

FEATURES = ["bold", "italic", "link", "h2", "hr"]
SAMPLE_HTML = '<p>Hello <b>world</b> <a href="https://openstax.org">here</a>.</p>'


def contentstate_for(html, features=FEATURES):
    return json.loads(ContentstateConverter(features).from_database_format(html))


def editor_options(features=FEATURES):
    # Wagtail's options hold lazy translations; the browser only ever sees them
    # after DjangoJSONEncoder has been through them, so match that here.
    options = DraftailRichTextArea(features=features).options
    return json.loads(json.dumps(options, cls=DjangoJSONEncoder))


def fake_service(reply, recorder=None):
    def completion(messages, **kwargs):
        if recorder is not None:
            recorder.extend(messages)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=reply))]
        )

    return mock.Mock(return_value=SimpleNamespace(completion=completion))


class EditorOptionMappingTests(TestCase):
    def test_option_types_map_back_to_feature_names(self):
        # The browser knows 'BOLD' and 'header-two'; the converter needs
        # 'bold' and 'h2', and getting it wrong silently deletes markup.
        self.assertEqual(
            set(features_from_editor_options(editor_options())), set(FEATURES)
        )

    def test_unrecognised_options_fall_back_to_the_default_features(self):
        from wagtail.rich_text import features as feature_registry

        self.assertEqual(
            features_from_editor_options({"entityTypes": [{"type": "NOPE"}]}),
            list(feature_registry.get_default_features()),
        )

    def test_allowed_tags_come_from_the_feature_list(self):
        tags = allowed_tags(["bold", "link"])
        self.assertIn("<b>", tags)
        self.assertIn("<a>", tags)
        self.assertNotIn("<h2>", tags)


class RewriteContentstateTests(TestCase):
    def rewrite(self, reply, html=SAMPLE_HTML, recorder=None):
        with mock.patch(
            "ai_assist.rewrite.get_llm_service", fake_service(reply, recorder)
        ):
            return rewrite_contentstate(
                contentstate=contentstate_for(html),
                editor_options=editor_options(),
                brief="This text is on the page \"Give\".",
            )

    def test_inline_formatting_and_links_survive_the_round_trip(self):
        rewritten = self.rewrite(
            '<p>Hi <b>there</b> <a href="https://openstax.org">friend</a>.</p>'
        )

        block = rewritten["blocks"][0]
        self.assertEqual(block["text"], "Hi there friend.")
        self.assertEqual(
            [style["style"] for style in block["inlineStyleRanges"]], ["BOLD"]
        )
        self.assertEqual(len(block["entityRanges"]), 1)
        self.assertEqual(
            list(rewritten["entityMap"].values())[0]["data"]["url"],
            "https://openstax.org",
        )

    def test_the_prompt_carries_the_brief_and_the_fragment(self):
        messages = []
        self.rewrite("<p>Hi.</p>", recorder=messages)

        system, user = messages
        self.assertIn('This text is on the page "Give".', system["content"])
        self.assertIn("OpenStax", system["content"])
        self.assertIn("Hello", user["content"])

    def test_code_fences_are_stripped(self):
        rewritten = self.rewrite("```html\n<p>Fenced.</p>\n```")

        self.assertEqual(rewritten["blocks"][0]["text"], "Fenced.")

    def test_markup_the_field_does_not_allow_is_dropped(self):
        rewritten = self.rewrite(
            "<p>Kept.</p><table><tr><td>Nope</td></tr></table>"
            "<h1>Also nope</h1><script>alert(1)</script>"
        )

        types = {block["type"] for block in rewritten["blocks"]}
        self.assertEqual(types, {"unstyled"})
        self.assertNotIn("header-one", types)

    def test_a_reply_with_nothing_usable_is_an_error(self):
        with self.assertRaises(RewriteError):
            self.rewrite("   ")

    def test_an_empty_fragment_is_an_error(self):
        with self.assertRaises(RewriteError):
            self.rewrite("<p>anything</p>", html="<p></p>")

    def test_an_oversized_fragment_is_an_error(self):
        with self.assertRaises(RewriteError):
            self.rewrite("<p>ok</p>", html=f"<p>{'x' * MAX_HTML_CHARS}</p>")

    def test_a_provider_failure_becomes_a_rewrite_error(self):
        service = mock.Mock(
            return_value=SimpleNamespace(
                completion=mock.Mock(side_effect=RuntimeError("boom"))
            )
        )
        with mock.patch("ai_assist.rewrite.get_llm_service", service):
            with self.assertRaises(RewriteError):
                rewrite_contentstate(
                    contentstate=contentstate_for(SAMPLE_HTML),
                    editor_options=editor_options(),
                    brief="",
                )


class BuildBriefTests(TestCase):
    def setUp(self):
        root = Page.objects.get(title="Root")
        self.page = GeneralPage(
            title="Give",
            slug="give-brief",
            body=[
                ("heading", "Give today"),
                ("paragraph", RichText("<p>Every gift keeps our books free.</p>")),
            ],
        )
        root.add_child(instance=self.page)

    def test_brief_names_the_page_and_quotes_its_other_copy(self):
        brief = build_brief(page_id=self.page.pk, field_label="Body")

        self.assertIn('"Give"', brief)
        self.assertIn("Body", brief)
        self.assertIn("Every gift keeps our books free.", brief)

    def test_brief_says_so_when_the_page_is_unknown(self):
        self.assertIn("do not know", build_brief(page_id=None))


class RewriteViewTests(TestCase, WagtailTestUtils):
    def setUp(self):
        self.url = reverse("ai_assist_rewrite")
        self.payload = {
            "contentstate": contentstate_for(SAMPLE_HTML),
            "editorOptions": editor_options(),
            "pageId": None,
            "fieldLabel": "Text",
        }

    def post(self, payload):
        return self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

    def test_admin_access_is_required(self):
        response = self.post(self.payload)

        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_editor_gets_the_rewritten_contentstate(self):
        self.login()
        with mock.patch(
            "ai_assist.rewrite.get_llm_service", fake_service("<p>Rewritten.</p>")
        ):
            response = self.post(self.payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["contentstate"]["blocks"][0]["text"], "Rewritten."
        )

    def test_a_malformed_payload_is_rejected(self):
        self.login()

        self.assertEqual(self.post({"contentstate": "nope"}).status_code, 400)

    def test_a_rewrite_error_comes_back_as_a_message(self):
        self.login()
        with mock.patch("ai_assist.rewrite.get_llm_service", fake_service("")):
            response = self.post(self.payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_get_is_not_allowed(self):
        self.login()

        self.assertEqual(self.client.get(self.url).status_code, 405)


class AdminAssetTests(TestCase):
    def test_the_control_script_is_injected_with_its_endpoint(self):
        from ai_assist.wagtail_hooks import ai_assist_draftail_js

        markup = ai_assist_draftail_js()

        self.assertIn("ai_assist/draftail_rewrite.js", markup)
        self.assertIn(reverse("ai_assist_rewrite"), markup)
