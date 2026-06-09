from django.test import TestCase

from openstax.settings import base


class WagtailAIConfigTests(TestCase):
    # Read base, not settings: test settings override the backends to EchoBackend.
    def test_base_config_defines_default_and_quality_llm_backends(self):
        backends = base.WAGTAIL_AI["BACKENDS"]
        self.assertIn("default", backends)
        self.assertIn("quality", backends)
        for name in ("default", "quality"):
            self.assertEqual(
                backends[name]["CLASS"],
                "wagtail_ai.ai.llm.LLMBackend",
            )
            self.assertIn("MODEL_ID", backends[name]["CONFIG"])

    def test_wagtail_ai_is_always_installed(self):
        # wagtail-ai is unconditionally enabled (no toggle) — see ai_assist/README.
        self.assertIn("wagtail_ai", base.INSTALLED_APPS)
