# ai_assist — Wagtail AI integration

AI-assisted authoring for the OpenStax CMS via [wagtail-ai] 3.x (built on
django-ai-core + any-llm). Always enabled; the tools only appear in the editor,
so anyone with Wagtail edit access can use them. Features:

- **Rich-text wand** — rewrite/grammar/completion in rich-text fields.
- **Title & meta-description suggestions** — on every page type (`AITitleFieldPanel` / `AIDescriptionFieldPanel`, applied in `panel_patches.py`).
- **Image alt text** — in the image editor (`WAGTAILIMAGES_IMAGE_FORM_BASE`) and contextually in StreamField image blocks (`AIImageBlock`).
- **Content feedback** — quality suggestions in the Checks side panel.
- **Related pages** — semantic suggestions on NewsArticle, Book, and FlexPage.

## Architecture
- Rich-text editor uses the legacy `WAGTAIL_AI["BACKENDS"]` (the `llm` library + `llm-anthropic`).
- Agent features (title/description, content feedback, image description) use `WAGTAIL_AI["PROVIDERS"]` (any-llm).
- Related pages use a `django_ai_core` `VectorIndex` (`PageVectorIndex`) with pgvector storage; embeddings via OpenAI.

## Environment variables
| Var | Purpose | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude — rich-text backends and the default agent provider. **Required.** | — |
| `OPENAI_API_KEY` | OpenAI — required for related-pages **embeddings**, and the optional `openai` backend. | — |
| `WAGTAIL_AI_AGENT_MODEL` | Claude model for agent features. | `claude-sonnet-4-6` |
| `WAGTAIL_AI_EMBEDDING_MODEL` | OpenAI embedding model. **Must stay 1536-dim** (e.g. `text-embedding-3-small`/`-ada-002`); the `vector` column is fixed at 1536. Switching to a different-dimension model (e.g. `text-embedding-3-large`, 3072) also requires editing `VectorField(dimensions=...)` in `ai_assist/models.py` and adding a migration, or inserts will fail. | `text-embedding-3-small` |
| `WAGTAIL_AI_DEFAULT_MODEL` / `WAGTAIL_AI_QUALITY_MODEL` / `WAGTAIL_AI_OPENAI_MODEL` | Rich-text backend model IDs. | haiku-4-5 / sonnet-4-6 / gpt-4o-mini |

## Deploy steps
1. Set `ANTHROPIC_API_KEY` (and `OPENAI_API_KEY` for related pages).
2. `python manage.py migrate` — creates the django_ai_core index tables, the `vector` extension, and the related-page relations. **Production Postgres must allow `CREATE EXTENSION vector`.**
3. `collectstatic` so the wagtail-ai admin JS is served.
4. `python manage.py seed_ai_prompts` (idempotent).
5. `python manage.py rebuild_indexes` — builds the embeddings for related-pages suggestions (re-run after large content changes).

## The `ai` rich-text feature
The wand only renders on editors whose feature list includes `"ai"`. wagtail-ai
adds it to `default_features`, but this project pins an explicit list in
`WAGTAILADMIN_RICH_TEXT_EDITORS`, so `"ai"` must stay in that list
(`tests/test_rich_text_features.py` guards it).

## Related pages
`PageVectorIndex` (in `vector_index.py`) indexes NewsArticle, Book, and FlexPage
(title + search_description). Each exposes a "Related pages" chooser
(`AIMultipleChooserPanel`) that suggests semantically-similar pages. RootPage (the
home singleton, and FlexPage's MTI base) is intentionally excluded. Embeddings are
created lazily, so the app boots without `OPENAI_API_KEY`; suggestions only work
once the key is set and `rebuild_indexes` has run.

## Manual QA (staging)
- [ ] Rich-text toolbar shows the AI wand + the seeded "Improve writing (OpenStax voice)" prompt.
- [ ] Title and meta-description fields show the AI suggestion button.
- [ ] Image editor offers alt-text generation; StreamField image blocks too.
- [ ] Content feedback appears in the Checks panel.
- [ ] After `rebuild_indexes`, the Related pages chooser suggests relevant pages.

[wagtail-ai]: https://github.com/wagtail/wagtail-ai
