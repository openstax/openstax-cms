from django.test import SimpleTestCase

from openstax.settings import base


class ContentFeedbackProviderTests(SimpleTestCase):
    """Content feedback is the only AI feature that requests structured output
    (``response_format``). any-llm 0.20.3's Anthropic provider rejects that, so
    we route content feedback to OpenAI — the same workaround already used for
    ``IMAGE_DESCRIPTION_PROVIDER``. Revert to the Anthropic ``default`` provider
    once any-llm is upgraded to >=1.x (its Anthropic provider supports it).
    """

    def test_base_config_defines_openai_content_feedback_provider(self):
        providers = base.WAGTAIL_AI["PROVIDERS"]
        self.assertIn("content_feedback", providers)
        self.assertEqual(providers["content_feedback"]["provider"], "openai")

    def test_content_feedback_agent_routed_off_default_provider(self):
        # ai_assist patches the agent (which hardcodes provider_alias="default")
        # to use the dedicated OpenAI provider; applied in AiAssistConfig.ready().
        from wagtail_ai.agents.content_feedback import ContentFeedbackAgent

        self.assertEqual(ContentFeedbackAgent.provider_alias, "content_feedback")
