# Flex Page Draft-Save API (Slice 1)

Endpoints that let an authenticated agent create and update `FlexPage`s as
**unpublished drafts** for a human to review and publish in the Wagtail admin.
**Nothing here ever publishes.**

> **Direction (2026-06-05):** the MCP server is moving **into the CMS** itself
> (`django-mcp-server` at `/mcp`, OAuth 2.1 + Dynamic Client Registration). The MCP
> tools will call the same service layer (`authoring/drafts.py`) that backs this
> REST endpoint, so this endpoint is a **transitional/secondary interface** —
> useful now for local testing while the in-CMS MCP is built.
>
> Status: Slice 1 (token auth). The request/response shapes below stay the same as
> we add OAuth2; only the `Authorization` header changes.

## Auth

Send a DRF token for a **staff** CMS user:

```
Authorization: Token <token>
```

Mint a token for a staff user (one-time, server side):

```bash
python3 manage.py drf_create_token <username>
```

- Only the `flex/` write endpoints require auth; the rest of `/apps/cms/api/v2/`
  stays public read.
- The user must be `is_staff` **and** have Wagtail add/edit rights on the target
  location (superusers always qualify). Otherwise: `403`.

## Create — `POST /apps/cms/api/v2/pages/flex/`

```jsonc
{
  "parent_id": 3,                                   // REQUIRED. Must be the site root (RootPage).
  "title": "Why OpenStax works for student learning",
  "slug": "why-openstax-student-learning",
  "layout": [{ "type": "default", "value": {} }],   // REQUIRED, exactly one block (see Layout)
  "body": [                                         // array of top-level StreamField nodes (see Body)
    { "type": "html", "value": "<p>Great for students</p>" }
  ]
}
```

**Success — `201`:**

```jsonc
{
  "id": 42,
  "slug": "why-openstax-student-learning",
  "live": false,                                    // ALWAYS false — never auto-published
  "edit_url": "/admin/pages/42/edit/",
  "preview_url": "/admin/pages/42/edit/preview/",
  "warnings": []
}
```

## Update — `PATCH /apps/cms/api/v2/pages/flex/<id>/`

Send any of `title`, `layout`, `body`. Saves a **new draft revision**; the live
published version is left untouched until a human publishes.

```jsonc
{ "title": "New draft title", "body": [ { "type": "html", "value": "<p>changed</p>" } ] }
```

Returns `200` with the same payload shape as create. Slug is **not** changed via
PATCH.

## Layout (required, explicit)

Exactly one block — the agent must choose intentionally:

- `{"type": "default", "value": {}}` — standard page **with** site nav.
- `{"type": "landing", "value": {"nav_links": [...], "show_give_now_button": true}}` —
  landing page (custom nav).

A missing/empty `layout`, or more than one block, is a `400`.

## Body (StreamField nodes)

`body` is an array of nodes shaped exactly like the read API returns and Tom's
`flex-page-renderer` consumes:

```jsonc
{ "type": "<block key>", "id": "<optional uuid>", "value": <data> }
```

**Valid TOP-LEVEL body blocks:** `hero`, `section`, `columns`, `divider`,
`html`, `tabbed_content`.

> Rich text (`text`) is **not** a top-level block — it lives *inside* a structural
> block (`section`/`hero`/`columns` → their `content`). To place a paragraph,
> wrap it: `{"type":"section","value":{"content":[{"type":"text","value":"<p>…</p>"}], "config":[]}}`.

An **empty** `body` (`[]`) is allowed — a draft can be built incrementally.

Validation is **server-authoritative**: the payload is checked against the real
`FlexPage` block definitions (the same rules the Wagtail editor enforces).
Unknown block types and invalid block data return `400` with a per-field,
correctable error map.

## Images

Reference images **by id** inside image blocks. Find them via the existing read
endpoint:

```
GET /apps/cms/api/v2/images/?search=<query>
```

Each item has top-level `id` and `title`; `download_url` (and `tags`, dimensions)
are under `meta`. Embed the `id` in the block value.

## Slugs & routing (important)

- Slugs are **global** on openstax.org — FlexPage URLs flatten to `/<slug>`
  regardless of tree depth, and the slug resolves site-wide.
- **Collision:** if the slug already exists anywhere in the tree, the draft is
  still created with a numeric suffix (`-1`, `-2`) **and** a warning is returned:

  ```jsonc
  "warnings": [{
    "code": "slug_collision",
    "message": "A page with slug 'dup' already exists in the site tree. Created as 'dup-1' instead. …",
    "existing_page_id": 17,
    "existing_page_edit_url": "/admin/pages/17/edit/"
  }]
  ```
  When you see this, you almost certainly want to **PATCH the existing page**
  instead of creating a near-duplicate.
- **Reserved slugs** (owned by nginx, redirects, or the frontend router) are
  rejected with `400` — a page there would be silently shadowed. Examples:
  `books`, `give`, `blog`, `accounts`, `subjects`, `k12`, `license`, `privacy`,
  `careers`, `api`, `admin`, … (see `authoring/routing_rules.py` for the full set;
  the deploy `uri-map` may add more — known follow-up).

## Reference & lock safety

- **Rich-text references are validated.** Every `<a linktype="page" id="N">` and
  `<embed embedtype="image" id="N">` must point to a real object; stale/hallucinated
  IDs are rejected (`400`, `errors.references.missing`). Look IDs up first via page /
  `?search=` image lookups. (External `<a href="…">` links are not checked.)
- **Locked pages are refused.** A `PATCH` to a Wagtail-locked page returns `409`.

## Error shape

```jsonc
// 400
{ "errors": { "body": { "0": ["…message…"] } } }
{ "errors": { "slug": "'books' is a reserved route … Choose another slug." } }
{ "errors": { "parent_id": "Unknown or missing parent_id." } }
{ "errors": { "references": { "message": "…", "missing": { "page": [999999], "image": [42] } } } }
// 401 / 403 — missing/insufficient credentials
// 409 — page is locked by another user (PATCH)
```

## Guarantees

- The endpoint **never publishes**. `live` is always `false` on the returned page;
  updates never alter the live version.
- A human reviews and publishes in the Wagtail admin (`edit_url`).
