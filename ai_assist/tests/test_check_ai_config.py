from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class CheckAiConfigTests(TestCase):
    """Test settings point PROVIDERS at a non-routable sentinel and set no API
    keys, so this doubles as proof the command reports a broken config loudly
    rather than exiting clean."""

    def test_broken_config_is_reported_and_exits_nonzero(self):
        out = StringIO()

        with self.assertRaises(SystemExit) as ctx:
            call_command("check_ai_config", stdout=out)
        output = out.getvalue()

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("FAIL  env ANTHROPIC_API_KEY: missing", output)
        for alias in ("default", "image_description", "embedding"):
            self.assertIn(f"FAIL  provider {alias}", output)
        self.assertIn("ok    seeded prompts", output)
