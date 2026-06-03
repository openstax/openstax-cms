from django.test import TestCase

from openstax.settings import base


class WagtailAIConfigTests(TestCase):
    # Assert the BASE module config directly, not settings.WAGTAIL_AI. Test
    # settings (a later task) override the active config to EchoBackend, so
    # reading `settings` here would contradict that. The base module is the
    # source of truth for the production backend wiring.
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

    def test_toggle_off_excludes_wagtail_ai_from_installed_apps(self):
        # When WAGTAIL_AI_ENABLED is false, the editor integration must not load.
        apps_when_off = base.build_installed_apps(ai_enabled=False)
        apps_when_on = base.build_installed_apps(ai_enabled=True)
        self.assertNotIn("wagtail_ai", apps_when_off)
        self.assertIn("wagtail_ai", apps_when_on)
