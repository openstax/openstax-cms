# ai_assist — Wagtail AI integration

AI-assisted authoring for the OpenStax CMS via [wagtail-ai]: image alt text,
in-editor writing help, and content feedback. It is **always enabled** — there
is no on/off toggle and no per-user gating. The AI tools only appear inside the
page/image editor, so anyone with Wagtail edit access can use them.

## Environment variables
| Var | Purpose | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API key (read by the `llm-anthropic` plugin). **Required.** | — |
| `OPENAI_API_KEY` | OpenAI API key (only needed if the `openai` backend is used). | — |
| `WAGTAIL_AI_DEFAULT_MODEL` | Override the cheap/high-volume model ID. | `anthropic/claude-haiku-4-5-20251001` |
| `WAGTAIL_AI_QUALITY_MODEL` | Override the stronger model ID. | `anthropic/claude-sonnet-4-6` |
| `WAGTAIL_AI_OPENAI_MODEL` | Override the OpenAI backend model ID. | `gpt-4o-mini` |

## Deploy steps
1. Set `ANTHROPIC_API_KEY` in the target environment.
2. Run `collectstatic` so `wagtail_ai/draftail.js` is served (part of the normal
   deploy). The magic-wand control will not load without it.
3. Run `python manage.py seed_ai_prompts` (idempotent — safe to re-run every deploy).

## The magic-wand control requires the `ai` rich-text feature
The AI wand only appears on rich-text editors whose feature list includes `"ai"`.
wagtail-ai auto-adds `"ai"` to Wagtail's `default_features`, **but this project
pins an explicit features list** in `WAGTAILADMIN_RICH_TEXT_EDITORS` (settings),
which overrides the defaults. `"ai"` is included there — if you ever edit that
list, keep `"ai"` in it or the wand silently disappears.
(`ai_assist/tests/test_rich_text_features.py` guards this.)

## Backends
- `default` → `anthropic/claude-haiku-4-5-20251001` — cheap, high-volume (alt text, grammar).
- `quality` → `anthropic/claude-sonnet-4-6` — stronger (content feedback, rewrites).
- `openai` → `gpt-4o-mini` — alternate provider (set `OPENAI_API_KEY` to use). Selectable per prompt/feature.
- Image alt text is routed to `default` via `WAGTAIL_AI["IMAGE_DESCRIPTION_BACKEND"]`.
  (This key has no built-in default in wagtail-ai 2.1.0 — it must be set or the
  feature raises BackendNotFound.)

## Manual QA checklist (run on staging)
- [ ] The rich-text toolbar shows the AI (magic-wand) action and the seeded
      "Improve writing (OpenStax voice)" prompt.
- [ ] Running an AI rewrite returns on-voice text and does not corrupt the field.
- [ ] Image edit view offers AI alt-text generation; output is ≤125 chars and factual.
- [ ] Content feedback returns suggestions without modifying the page.
- [ ] Provider dashboard (Anthropic) shows the expected token usage and no surprises.

[wagtail-ai]: https://github.com/wagtail/wagtail-ai
