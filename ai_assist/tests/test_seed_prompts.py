from django.core.management import call_command
from django.test import TestCase

from wagtail_ai.models import Prompt

from ai_assist.prompts import OPENSTAX_PROMPTS


class SeedAIPromptsTests(TestCase):
    def test_command_creates_all_brand_prompts(self):
        call_command("seed_ai_prompts")
        labels = set(Prompt.objects.values_list("label", flat=True))
        for spec in OPENSTAX_PROMPTS:
            self.assertIn(spec["label"], labels)

    def test_command_is_idempotent(self):
        call_command("seed_ai_prompts")
        call_command("seed_ai_prompts")
        for spec in OPENSTAX_PROMPTS:
            self.assertEqual(
                Prompt.objects.filter(label=spec["label"]).count(),
                1,
                msg=f"duplicate prompt created for {spec['label']!r}",
            )
