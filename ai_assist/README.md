# ai_assist — Wagtail AI integration

AI-assisted authoring for the OpenStax CMS via [wagtail-ai] 3.x (built on
django-ai-core + any-llm). Always enabled; the tools only appear in the editor,
so anyone with Wagtail edit access can use them. Features:

- **Rich-text wand** — rewrite/grammar/completion in rich-text fields.
- **OpenStax voice rewrite** — a second toolbar button that rewrites the
  selected blocks with page context, keeping the field's own markup.
- **Title & meta-description suggestions** — on every page type (`AITitleFieldPanel` / `AIDescriptionFieldPanel`, applied in `panel_patches.py`).
- **Image alt text** — in the image editor (`WAGTAILIMAGES_IMAGE_FORM_BASE`) and contextually in StreamField image blocks (`AIImageBlock`).
- **Content feedback** — quality suggestions in the Checks side panel. Reads
  the previewed page through Wagtail's userbar, so it needs the headless userbar
  wired up (see below); the other features work without it.
- **Related pages** — semantic suggestions on NewsArticle, Book, and FlexPage.

## Headless preview & the userbar
We render the front-end out of process (os-webview), so the field-level AI tools
above run entirely in the Wagtail admin and need nothing on the front-end. The
**Checks panel** (content checker, content metrics, accessibility checker, and
wagtail-ai's content checks) is different: it reads the previewed page via the
userbar's preview controller, which only exists if the userbar is loaded on the
front-end. Without it, content extraction returns `null`
([wagtail-ai#161](https://github.com/wagtail/wagtail-ai/issues/161)).

Two pieces make it work; both share an origin, so no CORS is involved:
- **CMS** — `RootPage.serve_preview` redirects previews to the front-end URL
  (no nested iframe), and `HeadlessUserbarView` (`pages/views.py`, routed at
  `/apps/cms/api/userbar/` — the only `/apps/cms/` path production nginx routes
  to this backend) serves the userbar markup, gated to admins.
- **os-webview** — the `HeadlessUserbar` component fetches that endpoint while
  `?preview` is in the URL, injects the markup, and loads Wagtail's
  `vendor.js`/`userbar.js`.

## Architecture
- Rich-text editor uses the legacy `WAGTAIL_AI["BACKENDS"]` (the `llm` library + `llm-anthropic`).
- Agent features (title/description, content feedback, image description) use `WAGTAIL_AI["PROVIDERS"]` (any-llm).
- Related pages use a `django_ai_core` `VectorIndex` (`PageVectorIndex`) with pgvector storage; embeddings via OpenAI.

### Provider routing
All agent features run on Anthropic. Two aliases exist for cost, not capability:
- **`default`** (Sonnet) — title/description suggestions, content feedback.
- **`image_description`** (Haiku, via `IMAGE_DESCRIPTION_PROVIDER`) — alt text is cheap and high-volume, so it gets the smaller model.
- **`embedding`** — OpenAI, because Anthropic has no embedding models.

Until any-llm 1.x (see below), image description and content feedback were both
forced onto OpenAI: 0.20.3's Anthropic provider didn't translate OpenAI
`image_url` blocks and rejected `response_format`. 1.23 converts `image_url` to
Anthropic's `image`/`source` and maps `response_format` to `output_config`, so
both features run on Claude and `ai_assist/agent_patches.py` is gone.

Note: any-llm's Anthropic provider still rejects `response_format={"type":
"json_object"}`. `ContentFeedbackAgent` passes a Pydantic model
(`ContentFeedbackSchema`), which takes the supported JSON-schema path.

### Upgrading any-llm
`any-llm-sdk` is pinned transitively by `django-ai-core` (exact pin before
0.1.6, `>=1.23.0,<2` since). Bump both together in `requirements/base.txt` or
pip resolves to a conflict.

## Environment variables
| Var | Purpose | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude — rich-text backends and the default agent provider. **Required.** | — |
| `OPENAI_API_KEY` | OpenAI — required for related-pages **embeddings**, and the optional `openai` backend. | — |
| `WAGTAIL_AI_AGENT_MODEL` | Claude model for agent features. | `claude-sonnet-4-6` |
| `WAGTAIL_AI_IMAGE_DESCRIPTION_MODEL` | Claude model for alt-text generation (cheaper than the default — see Provider routing). | `claude-haiku-4-5-20251001` |
| `WAGTAIL_AI_EMBEDDING_MODEL` | OpenAI embedding model. **Must stay 1536-dim** (e.g. `text-embedding-3-small`/`-ada-002`); the `vector` column is fixed at 1536. Switching to a different-dimension model (e.g. `text-embedding-3-large`, 3072) also requires editing `VectorField(dimensions=...)` in `ai_assist/models.py` and adding a migration, or inserts will fail. | `text-embedding-3-small` |
| `WAGTAIL_AI_DEFAULT_MODEL` / `WAGTAIL_AI_QUALITY_MODEL` / `WAGTAIL_AI_OPENAI_MODEL` | Rich-text backend model IDs. BACKENDS use the `provider/model` format the `llm` library requires; the PROVIDERS rows above use a bare model id because the provider is a separate field. | `anthropic/claude-haiku-4-5-20251001` / `anthropic/claude-sonnet-4-6` / `gpt-4o-mini` |

## Deploy steps
1. Set `ANTHROPIC_API_KEY` (and `OPENAI_API_KEY` for related pages).
2. `python manage.py migrate` — creates the django_ai_core index tables, the `vector` extension, and the related-page relations. **Production Postgres must allow `CREATE EXTENSION vector`.**
3. `collectstatic` so the wagtail-ai admin JS is served.
4. `python manage.py seed_ai_prompts` (idempotent).
5. `python manage.py rebuild_indexes` — builds the embeddings for related-pages suggestions (re-run after large content changes).
6. `python manage.py check_ai_config` — one live call per configured provider and
   backend, plus the admin assets and seeded prompts. Exits non-zero and names
   what broke. Run it on the box after every deploy: the editor UI shows a
   generic error (or nothing at all) for a missing key, an un-collected asset, or
   an unknown model id, so a green deploy tells you nothing about whether the AI
   features actually work.

Secrets reach the instance from SSM at `/shared/cms/` and `/<env>/cms/`
(`bit-deployment`'s `update-secrets.py` uppercases each name into an env var), so
`ANTHROPIC_API_KEY` and `OPENAI_API_KEY` must exist under one of those paths.

## The `ai` rich-text feature
The wand only renders on editors whose feature list includes `"ai"`. wagtail-ai
adds it to `default_features`, but this project pins an explicit list in
`WAGTAILADMIN_RICH_TEXT_EDITORS`, so `"ai"` must stay in that list
(`tests/test_rich_text_features.py` guards it).

## OpenStax voice rewrite
Our own Draftail control, separate from wagtail-ai's wand, because the wand
posts `getPlainText()` and pastes the reply back as plain text: it cannot see
where the field sits and it destroys links, emphasis, and block structure.

The button rewrites the blocks the selection touches (the whole field when
nothing is selected) and leaves everything else alone.

- **No HTML crosses the wire.** The browser sends ContentState; the server
  converts with Wagtail's own `ContentstateConverter`, so the field's real
  feature list is applied in both directions and markup the model invents but
  the field does not allow is dropped on the way back in. `draftail_features.py`
  recovers that feature list by mapping the editor's option types (`BOLD`,
  `header-two`) back to Wagtail feature names — converting with a narrower list
  than the field allows would silently delete the editor's own markup.
- **Context** (`rewrite_context.py`) comes from the *saved* page: title, page
  type, the field's label, and the neighbouring copy. Unsaved edits are
  invisible to it, which is fine — it is tone context, not source material.
- **Voice** (`prompts.py`: `VOICE_RULES`, `VOICE_EXEMPLARS`, `voice_prompt`) is
  static exemplars, not retrieval. `PageVectorIndex` embeds titles and meta
  descriptions only, and retrieving from our own body copy would teach the model
  the voice we are trying to move away from.
- **Provider** is the any-llm `default` alias (Sonnet), not the legacy `llm`
  BACKENDS path.

Pieces: `views.py` (`/admin/ai-assist/rewrite/`), `rewrite.py`,
`rewrite_context.py`, `draftail_features.py`, `wagtail_hooks.py`,
`static/ai_assist/draftail_rewrite.js`. Tests in `tests/test_rewrite.py`; the JS
has no test harness in this repo, so the editor side is checked by hand.

## Related pages
`PageVectorIndex` (in `vector_index.py`) indexes NewsArticle, Book, and FlexPage
(title + search_description). Each exposes a "Related pages" chooser
(`AIMultipleChooserPanel`) that suggests semantically-similar pages. RootPage (the
home singleton, and FlexPage's MTI base) is intentionally excluded. Embeddings are
created lazily, so the app boots without `OPENAI_API_KEY`; suggestions only work
once the key is set and `rebuild_indexes` has run.

## Manual QA (staging)
- [ ] `python manage.py check_ai_config` passes.
- [ ] Rich-text toolbar shows the AI wand + the seeded "Improve writing (OpenStax voice)" prompt.
- [ ] The OpenStax voice button rewrites a selection, keeps its links and bold, and leaves the rest of the field alone.
- [ ] Title and meta-description fields show the AI suggestion button.
- [ ] Image editor offers alt-text generation; StreamField image blocks too.
- [ ] Content feedback appears in the Checks panel.
- [ ] After `rebuild_indexes`, the Related pages chooser suggests relevant pages.

[wagtail-ai]: https://github.com/wagtail/wagtail-ai
