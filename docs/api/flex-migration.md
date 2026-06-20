# FlexPage Migration API (Stopgap)

Export a `FlexPage`'s live content from one CMS environment and import it as an
**unpublished draft** on another — so an editor can re-add blanked references and
publish in the Wagtail admin.

> **Why this exists:** `wagtail-transfer` requires environments to be re-seeded from
> prod and fully pre-seeded before it can move pages. Until that setup is ready, this
> two-endpoint HTTP round-trip is the supported path for moving FlexPages between
> dev → staging → prod.
>
> **What this does NOT replace:** creating and editing drafts via the agent authoring
> API (`POST /apps/cms/api/v2/pages/flex/` and `PATCH …/<id>/`). Those endpoints use
> strict reference validation and are documented in `docs/api/flex-draft-save.md`.

## Auth

Both endpoints require a DRF token for a **staff** CMS user on the respective
environment:

```
Authorization: Token <token>
```

Mint a token for a staff user (one-time, server side):

```bash
python3 manage.py drf_create_token <username>
```

- Only staff users with Wagtail add rights qualify. Superusers always qualify.
- Missing or insufficient credentials: `401` / `403`.

## Export — `GET /apps/cms/api/v2/pages/flex/<id>/export/`

Reads the page's **live** field values (not the latest draft revision) and returns
them sanitized and import-ready. The sanitizer blanks all cross-environment object
references (see [Reference blanking](#reference-blanking)) while preserving all text,
structure, and config.

### Response

**`200`:**

```jsonc
{
  "title": "Why OpenStax Works",
  "slug": "why-openstax-works",
  "layout": [{ "type": "default", "value": {} }],
  "body": [
    { "type": "html", "id": "abc123", "value": "<p>Great for students</p>" }
    // chooser block values (images, snippets, etc.) are null here — blanked by sanitizer
  ]
}
```

The four fields match the import endpoint's request body exactly. Pass this JSON
directly to the import endpoint (adding `parent_id`).

**`404`:**

```jsonc
{ "errors": { "page_id": "Unknown FlexPage." } }
```

Returned when the `id` does not exist or does not belong to a FlexPage.

## Import — `POST /apps/cms/api/v2/pages/flex/import/`

Creates an **unpublished draft** from migrated FlexPage JSON. Uses lenient
validation: block **types** are checked (unknown block types → `400`), but layout
cardinality (exactly one `default`/`landing` block), required-field checks, and
rich-text reference checks are **deferred to publish time** (because the sanitizer
blanks references, and a blanked chooser saves fine as a draft).

Routing rules are the same as the regular create endpoint: reserved slugs are
rejected, only `RootPage` parents are allowed, and slug collisions are suffixed with
a warning.

### Request

```jsonc
{
  "parent_id": 30,                              // REQUIRED. Must be the site root (RootPage) on the TARGET env.
  "title": "Why OpenStax Works",
  "slug": "why-openstax-works",
  "layout": [{ "type": "default", "value": {} }],
  "body": [ /* sanitized body from the export */ ]
}
```

`parent_id` must be an integer (the page id of the target `RootPage`).
A missing, non-integer, or unknown value returns `400`.

### Response

**`201` — draft created:**

```jsonc
{
  "id": 42,
  "slug": "why-openstax-works",
  "live": false,           // ALWAYS false — never auto-published
  "edit_url": "/admin/pages/42/edit/",
  "preview_url": "/admin/pages/42/edit/preview/",
  "warnings": []           // non-empty if the slug was suffixed due to collision
}
```

## Reference blanking

Cross-environment object references cannot survive a move between environments
because images, documents, snippets, and pages have different database ids in each
environment. The sanitizer blanks them while keeping everything else.

| Content | What happens |
|---|---|
| **Text / HTML / structure / config** | Preserved as-is |
| **Chooser blocks** (image, document, snippet, page, book-list, FAQ) | Set to `null` |
| **Rich-text page links** (`<a linktype="page">`) | Unwrapped to their inner text |
| **Rich-text image embeds** (`<embed embedtype="image">`) | Removed entirely |

The sanitizer is driven by the actual FlexPage block definitions (same
source-of-truth approach as the authoring service layer), so it handles nested
choosers inside `StructBlock`, `StreamBlock`, and `ListBlock` without a hardcoded
field-name list.

### After import: required human steps

The import **never publishes**. Before the page is ready to go live, an editor must:

1. Open the draft in the Wagtail admin (`edit_url` from the import response).
2. Re-add all blanked references: images, document links, snippet choosers, and
   rich-text page links.
3. Review all content for correctness in the target environment.
4. Publish the page from the Wagtail admin.

## Error shapes

```jsonc
// 400 — parent missing, non-integer, or not found
{ "errors": { "parent_id": "Unknown or missing parent_id." } }

// 400 — reserved slug
{ "errors": { "slug": "Invalid page location or slug." } }

// 400 — unknown block type (the key is the field that carried it: "body" or "layout")
{ "errors": { "body": "Unknown block type(s): ['not_a_block']. Allowed: [...]." } }
{ "errors": { "layout": "Unknown block type(s): ['not_a_block']. Allowed: [...]." } }

// 401 / 403 — missing or insufficient credentials
// 404 — id does not exist or is not a FlexPage (export endpoint)
```

Slug collision is NOT a hard error — the draft is created with a numeric suffix
(`-1`, `-2`, …) and a `slug_collision` warning is returned in the `warnings` array:

```jsonc
"warnings": [{
  "code": "slug_collision",
  "message": "A page with slug 'why-openstax-works' already exists in the site tree. Created as 'why-openstax-works-1' instead. …",
  "existing_page_id": 17,
  "existing_page_edit_url": "/admin/pages/17/edit/"
}]
```

When you see this, you almost certainly want to open the existing page instead.

## `flex_migrate.py` — CLI round-trip

`scripts/flex_migrate.py` runs the full export→import round-trip in one command.
It has no CMS dependencies and runs from any machine with `requests` installed.

```bash
python scripts/flex_migrate.py \
  --page-id 568 \
  --parent-id 30 \
  --source  https://dev.openstax.org/apps/cms/api/v2/pages/flex \
  --source-token "$DEV_TOKEN" \
  --target  https://staging.openstax.org/apps/cms/api/v2/pages/flex \
  --target-token "$STG_TOKEN"
```

On success it prints the new draft id and the admin edit URL:

```
Imported as draft id=42 (live=False).
Open and publish: /admin/pages/42/edit/
```

HTTP errors (non-2xx responses) are printed to stderr with the status code and
response body; the script exits with code `1`.

### Flags

| Flag | Required | Description |
|---|---|---|
| `--page-id` | Yes | Id of the FlexPage on the **source** environment |
| `--parent-id` | Yes | Id of the parent `RootPage` on the **target** environment |
| `--source` | Yes | Source flex API base URL (no trailing slash) |
| `--source-token` | Yes | Staff API token for the source environment |
| `--target` | Yes | Target flex API base URL (no trailing slash) |
| `--target-token` | Yes | Staff API token for the target environment |

## Guarantees

- The import endpoint **never publishes**. `live` is always `false` on the returned
  page; the live version on the target environment is never touched.
- A human reviews all content and re-adds blanked references before publishing.
- The script moves **one page at a time** — run it once per `--page-id`.
