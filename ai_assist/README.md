# ai_assist — Wagtail AI integration

AI-assisted authoring for the OpenStax CMS via [wagtail-ai]. Phase 1: image
alt text, in-editor writing help, content feedback.

## Environment variables
| Var | Purpose | Default |
|---|---|---|
| `WAGTAIL_AI_ENABLED` | Master switch / cost kill-switch. Set `true` to load AI in the editor. | `false` |
| `ANTHROPIC_API_KEY` | Claude API key (read by the `llm-claude-3` plugin). | — |
| `OPENAI_API_KEY` | OpenAI API key (optional, if an OpenAI backend is used). | — |
| `WAGTAIL_AI_DEFAULT_MODEL` | Override the cheap/high-volume model ID. | `anthropic/claude-haiku-4-5-20251001` |
| `WAGTAIL_AI_QUALITY_MODEL` | Override the stronger model ID. | `anthropic/claude-sonnet-4-6` |
| `WAGTAIL_AI_OPENAI_MODEL` | Override the OpenAI backend model ID. | `gpt-4o-mini` |

## Deploy steps
1. Set `WAGTAIL_AI_ENABLED=true` and `ANTHROPIC_API_KEY` in the target environment.
2. Run `python manage.py seed_ai_prompts` (idempotent — safe to re-run every deploy).

## Gating model (honest limits)
- **Master toggle** (`WAGTAIL_AI_ENABLED`): off → `wagtail_ai` is not in INSTALLED_APPS
  and no AI appears in the editor. Flip off to instantly stop all spend.
- **Who sees it**: AI tools only appear inside the page/image editor, so only users
  with Wagtail edit permissions ever see them. To pilot with a subset of editors,
  restrict edit access to the pilot group during the trial. wagtail-ai has no
  built-in per-feature permission, so this is the available gating lever.
- **Prompt curation**: only the seeded OpenStax prompts exist at launch.

## Backends
- `default` → `anthropic/claude-haiku-4-5-20251001` — cheap, high-volume (alt text, grammar).
- `quality` → `anthropic/claude-sonnet-4-6` — stronger (content feedback, rewrites).
- `openai` → `gpt-4o-mini` — alternate provider (set `OPENAI_API_KEY` to use). Selectable per prompt/feature.
- Image alt text is routed to `default` via `WAGTAIL_AI["IMAGE_DESCRIPTION_BACKEND"]`.
  (This key has no built-in default in wagtail-ai 2.1.0 — it must be set or the
  feature raises BackendNotFound.)

## Turning it off
Set `WAGTAIL_AI_ENABLED=false` and redeploy (or clear the env var). No data is lost;
seeded prompts remain in the DB for when it's re-enabled.

## Manual QA checklist (run on staging before widening the editor group)
- [ ] With `WAGTAIL_AI_ENABLED=false`, no AI buttons appear in the rich-text toolbar.
- [ ] With it `true`, the rich-text toolbar shows the AI action and the seeded
      "Improve writing (OpenStax voice)" prompt.
- [ ] Running an AI rewrite returns on-voice text and does not corrupt the field.
- [ ] Image edit view offers AI alt-text generation; output is ≤125 chars and factual.
- [ ] Content feedback returns suggestions without modifying the page.
- [ ] Provider dashboard (Anthropic) shows the expected token usage and no surprises.

[wagtail-ai]: https://github.com/wagtail/wagtail-ai
