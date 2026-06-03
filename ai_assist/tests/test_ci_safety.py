from django.conf import settings
from django.test import TestCase


class CISafetyTests(TestCase):
    def test_all_backends_use_echo_in_test_settings(self):
        # No backend in the test environment may point at a real LLM provider.
        for name, cfg in settings.WAGTAIL_AI["BACKENDS"].items():
            self.assertEqual(
                cfg["CLASS"],
                "wagtail_ai.ai.echo.EchoBackend",
                msg=f"backend '{name}' must use EchoBackend in tests",
            )

    def test_wagtail_ai_enabled_in_tests(self):
        # Feature code paths must be exercised, so the integration is on in CI.
        self.assertIn("wagtail_ai", settings.INSTALLED_APPS)
