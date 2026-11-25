import os

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Smoke-test every configured AI provider and backend with one live call, "
        "plus the admin assets and seeded prompts the editor UI needs."
    )

    def handle(self, *args, **options):
        failures = []

        for label, ok, detail in self._checks():
            if ok:
                self.stdout.write(self.style.SUCCESS(f"  ok    {label}: {detail}"))
            else:
                failures.append(label)
                self.stdout.write(self.style.ERROR(f"  FAIL  {label}: {detail}"))

        if failures:
            self.stdout.write(
                self.style.ERROR(f"\n{len(failures)} check(s) failed: {', '.join(failures)}")
            )
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("\nAll AI checks passed."))

    def _checks(self):
        yield from self._key_checks()
        yield from self._provider_checks()
        yield from self._backend_checks()
        yield self._static_check()
        yield self._prompt_check()

    def _key_checks(self):
        for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            value = os.getenv(var)
            yield (
                f"env {var}",
                bool(value),
                f"set ({len(value)} chars)" if value else "missing",
            )

    def _provider_checks(self):
        # The agent path (title/description, alt text, content feedback, embeddings).
        from wagtail_ai.agents import get_llm_service

        for alias in settings.WAGTAIL_AI.get("PROVIDERS", {}):
            label = f"provider {alias}"
            try:
                service = get_llm_service(alias=alias)
                if alias == "embedding":
                    result = service.embedding(["ping"])
                    detail = f"{service.service_id} -> {len(result.data[0].embedding)} dims"
                else:
                    result = service.completion(
                        [{"role": "user", "content": "Reply with OK."}], max_tokens=4
                    )
                    detail = f"{service.service_id} -> {result.choices[0].message.content!r}"
                yield label, True, detail
            except Exception as exc:
                yield label, False, f"{type(exc).__name__}: {exc}"

    def _backend_checks(self):
        # The legacy llm-library path behind the rich-text wand.
        from wagtail_ai.ai import get_ai_backend

        for alias in settings.WAGTAIL_AI.get("BACKENDS", {}):
            label = f"backend {alias}"
            try:
                response = get_ai_backend(alias).prompt_with_context(
                    pre_prompt="Reply with OK.", context="ping"
                )
                yield label, True, repr(response.text()[:60])
            except Exception as exc:
                yield label, False, f"{type(exc).__name__}: {exc}"

    def _static_check(self):
        # Every AI control is JS-driven, so an un-collected asset kills all of them
        # at once with no error in the editor.
        asset = "wagtail_ai/main.css"
        try:
            found = staticfiles_storage.exists(asset)
        except Exception as exc:
            return "static wagtail_ai", False, f"{type(exc).__name__}: {exc}"
        return (
            "static wagtail_ai",
            found,
            f"{asset} present" if found else f"{asset} missing — run collectstatic",
        )

    def _prompt_check(self):
        from wagtail_ai.models import Prompt

        count = Prompt.objects.count()
        return (
            "seeded prompts",
            count > 0,
            f"{count} prompt(s)" if count else "none — run seed_ai_prompts",
        )
