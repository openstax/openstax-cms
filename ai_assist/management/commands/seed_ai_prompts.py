from django.core.management.base import BaseCommand

from ai_assist.prompts import OPENSTAX_PROMPTS


class Command(BaseCommand):
    help = "Create or update the OpenStax brand-tuned wagtail-ai prompts."

    def handle(self, *args, **options):
        from django.conf import settings

        if not getattr(settings, "WAGTAIL_AI_ENABLED", False):
            self.stdout.write(
                self.style.WARNING(
                    "WAGTAIL_AI_ENABLED is false — wagtail_ai is not installed; skipping prompt seeding."
                )
            )
            return

        from wagtail_ai.models import Prompt

        method_map = {m.name: m.value for m in Prompt.Method}
        created, updated = 0, 0
        for spec in OPENSTAX_PROMPTS:
            defaults = {
                "description": spec["description"],
                "prompt": spec["prompt"],
                "method": method_map[spec["method"]],
            }
            obj, was_created = Prompt.objects.update_or_create(
                label=spec["label"], defaults=defaults
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded OpenStax prompts: {created} created, {updated} updated."
            )
        )
