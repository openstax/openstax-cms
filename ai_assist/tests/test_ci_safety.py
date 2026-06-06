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

    def test_all_providers_use_stub_in_test_settings(self):
        # The any-llm PROVIDERS tree (agent + embedding features) must not name a
        # real provider in tests, or a path that resolves a client could make a
        # billable API call. All providers must use the non-routable sentinel.
        stub = getattr(settings, "AI_TEST_STUB_PROVIDER", "openstax-test-stub")
        for name, cfg in settings.WAGTAIL_AI["PROVIDERS"].items():
            self.assertEqual(
                cfg["provider"],
                stub,
                msg=f"provider '{name}' must use the test stub provider, not a real LLM provider",
            )

    def test_wagtail_ai_installed(self):
        # wagtail-ai is always installed (no toggle); feature code paths run in CI.
        self.assertIn("wagtail_ai", settings.INSTALLED_APPS)
