"""Canary for the two any-llm behaviours that let all agents run on Anthropic.

Before any-llm 1.x, its Anthropic provider couldn't translate OpenAI-style
``image_url`` blocks and rejected ``response_format``, so image description and
content feedback had to be routed to OpenAI (see ai_assist/README.md). Those
conversions are what make the Anthropic-only PROVIDERS config work, and neither
is exercised by the rest of the suite — the test settings point every provider
at a non-routable stub, so no code path reaches them.

These call any-llm internals (``_convert_*``) on purpose: there is no public
conversion API short of a live completion. If an any-llm bump renames them, this
test errors, which is the signal we want before shipping the bump.
"""

from django.test import SimpleTestCase

from openstax.settings import base


class AnthropicImageBlockTests(SimpleTestCase):
    def test_openai_image_url_block_converts_to_anthropic_source(self):
        from any_llm.providers.anthropic.utils import _convert_messages_for_anthropic

        # The exact shape wagtail-ai's BasicPromptAgent.split_context_files builds.
        _, messages = _convert_messages_for_anthropic(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image"},
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64,AAAA"},
                        },
                    ],
                }
            ]
        )

        image_block = messages[0]["content"][1]
        self.assertEqual(image_block["type"], "image")
        self.assertEqual(
            image_block["source"],
            {"type": "base64", "media_type": "image/jpeg", "data": "AAAA"},
        )


class AnthropicStructuredOutputTests(SimpleTestCase):
    def test_content_feedback_schema_converts_to_output_config(self):
        from any_llm.providers.anthropic.utils import _convert_params
        from any_llm.types.completion import CompletionParams
        from wagtail_ai.agents.content_feedback import ContentFeedbackSchema

        kwargs = _convert_params(
            CompletionParams(
                model_id="claude-sonnet-4-6",
                messages=[{"role": "user", "content": "hi"}],
                response_format=ContentFeedbackSchema,
            ),
            provider_name="anthropic",
        )

        # Anthropic has no OpenAI-style JSON mode; 1.x maps the Pydantic schema
        # onto its own output_config instead of raising UnsupportedParameterError.
        self.assertEqual(kwargs["output_config"]["format"]["type"], "json_schema")
        self.assertIn("schema", kwargs["output_config"]["format"])

    def test_content_feedback_agent_passes_a_schema_not_json_object(self):
        # any-llm's Anthropic provider still rejects {"type": "json_object"}.
        # The agent passing a Pydantic model is what keeps it on the supported path.
        from pydantic import BaseModel
        from wagtail_ai.agents.content_feedback import ContentFeedbackAgent

        self.assertTrue(issubclass(ContentFeedbackAgent._response_format, BaseModel))


class AgentProviderRoutingTests(SimpleTestCase):
    def test_all_agent_providers_use_anthropic(self):
        # Embeddings are the one exception — Anthropic has no embedding models.
        providers = base.WAGTAIL_AI["PROVIDERS"]
        agent_providers = {
            name: cfg for name, cfg in providers.items() if name != "embedding"
        }
        self.assertTrue(agent_providers)
        for name, cfg in agent_providers.items():
            self.assertEqual(
                cfg["provider"],
                "anthropic",
                msg=f"agent provider '{name}' should run on Anthropic",
            )

    def test_image_description_provider_alias_is_configured(self):
        # Alt text runs on a cheaper model than the default agent provider.
        alias = base.WAGTAIL_AI["IMAGE_DESCRIPTION_PROVIDER"]
        self.assertIn(alias, base.WAGTAIL_AI["PROVIDERS"])
        self.assertNotEqual(
            base.WAGTAIL_AI["PROVIDERS"][alias]["model"],
            base.WAGTAIL_AI["PROVIDERS"]["default"]["model"],
        )
