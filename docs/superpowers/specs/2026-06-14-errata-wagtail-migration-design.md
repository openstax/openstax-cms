# Errata → native Wagtail admin (full parity) — design spec

**Date:** 06/14/2026
**Status:** Draft for review
**Phase:** 3 of the admin-menu reorganization (Phases 1 & 2 — menu reorg, modeladmin
retirement, snippet grouping, Partners native — are implemented on branch
`admin-menu-reorg`).

## Goal

Move Errata management fully into the Wagtail admin so editors stop bouncing to
`/django-admin/`, **without losing the workflow the team relies on every day**:
filtering (including date ranges) and exporting to CSV. Advanced/destructive
behaviour stays available but gated by **permission**, not hidden behind a second
admin URL.

## Why this is its own phase

Errata is the most complex admin in the codebase. Unlike Partners (a flat data
model), `errata/admin.py` layers on six interacting behaviours. A faithful port
touches Wagtail's form, filter, export, and permission systems at once, so it gets
its own spec rather than riding along with the menu reorg.

## Current behaviour to reproduce (from `errata/admin.py`)

| # | Feature | Today (Django admin) | Notes / risk |
|---|---------|----------------------|--------------|
| 1 | **List filters** | `book`, `status`, `error_type`, `resolution`, `archived`, `junk`, `is_assessment_errata`, plus **`DateRangeFilter`** on `created` & `modified` | Heavily used. Date-range is the tricky one in Wagtail. |
| 2 | **CSV export** | Two: (a) standard `import_export` `ErrataResource` (full field set); (b) custom **"Release Notes"** export — renamed columns `Location/Detail/Resolution Notes/Error Type` → `Release Notes.csv` | Both must work. Heavily used. |
| 3 | **Status actions** | `mark_in_review`, `mark_OpenStax_editorial_review`, `mark_cartridge_review`, `mark_reviewed`, `mark_archived`, `mark_completed` | Several gated to the **Content Managers** group. |
| 4 | **Per-group field & column visibility** | Content Managers / superuser, **Editorial Vendor**, and everyone-else each see different `list_display`, `list_filter`, form `fields`, and `readonly_fields` | The biggest faithfulness challenge. |
| 5 | **Inline internal docs** | `InternalDocumentation` images edited inline (`TabularInline`) | Needs an InlinePanel-style equivalent. |
| 6 | **Version history** | `django-reversion` `VersionAdmin` | Decision needed: keep reversion vs adopt Wagtail revisions. |
| | Misc | `raw_id_fields=('duplicate_id',)`, `save_as`, `list_per_page=200`, `ErrataForm`, `accounts_link`/`accounts_user_faculty_status` readonly helpers, superuser-only delete | |

The existing `ErrataModelViewSet` (`errata/views.py`) already provides basic
`list_display`, `list_filter`, `list_export`, and `search_fields` — a useful
starting skeleton but it implements none of #2(b), #3, #4, #5, #6.

## Proposed approach

A `ModelViewSet` for `Errata` registered via `register_admin_viewset`, replacing
both the Django-admin link and the `Errata (Beta)` stub. Built up feature by
feature:

### 1. Filters (incl. date range)
Use Wagtail's django-filter integration: define a `FilterSet` as the viewset's
`filterset_class` with `django_filters.DateFromToRangeFilter` for `created` and
`modified`, and standard filters for the rest. This replaces `rangefilter`.

### 2. CSV export (both)
- Standard export: Wagtail `list_export` + `export_filename` already yields
  CSV/XLSX download buttons — covers the full-field export.
- "Release Notes" export: add an extra view to the viewset (`get_urlpatterns`) that
  reuses the existing `CustomExportResource` and returns `Release Notes.csv`.
  Surface it as a header button on the index (permission-gated), mirroring the
  Partner "Sync" button pattern from Phase 2.

### 3. Status actions
Implement as Wagtail **bulk actions** (`register_bulk_action`, `models=[Errata]`).
**Open question:** generic `ModelViewSet` index views do **not** support bulk
actions (confirmed in Phase 2 — only snippets/pages do). Options:
  - (a) Per-row "Set status →" buttons via `IndexView.get_list_more_buttons` (no
    multi-select).
  - (b) A small custom multi-select action view.
  - (c) Register `Errata` as a snippet to unlock native bulk actions.
  Recommend (a) unless the team specifically needs multi-select status changes.

### 4. Per-group field/column visibility
Drive `list_display`, `list_filter`, and the edit panels off the request user's
group in the view layer:
- Override `get_list_display` / `get_filterset_class` on a custom `IndexView`.
- Override `get_edit_handler` / `get_form_class` per group on custom create/edit
  views (Content Managers & superuser, Editorial Vendor, default).
Encode the three field matrices from `errata/admin.py` as named panel sets.

### 5. Inline internal documentation
`InternalDocumentation` becomes an `InlinePanel` on the Errata edit handler
(requires the FK to expose a `related_name` and a `ClusterableModel`/`ParentalKey`
relationship — **may require a model change + migration**; to be confirmed during
implementation).

### 6. Version history — DECISION REQUIRED
- **Option A (less work):** keep `django-reversion` and add a permission-gated
  header button linking to a reversion history view.
- **Option B (more native):** add `RevisionMixin` to `Errata` and use Wagtail's
  revision UI. Larger change (model + migration + data considerations); historical
  reversion data would not carry over.
  Recommend **A** for parity now; revisit B later.

## Permissions model

- Editing/listing: any user with `errata.view_errata` / `errata.change_errata`.
- Status changes, archive, Release-Notes export, history: gated to **Content
  Managers** (and superusers), matching today's `get_actions`/`changelist_view`
  logic.
- Delete: superuser only.
- Editorial Vendor: restricted field set (no `junk`, limited readonly), per #4.

## Out of scope

- `BlockedUser`, `EmailText`, `InternalDocumentation` standalone admin (stay in
  Django admin unless trivially portable).
- Changing the errata submission/public API.

## Open decisions for the team

1. **Version history:** keep `django-reversion` (Option A) or migrate to Wagtail
   revisions (Option B)?
2. **Status changes:** per-row buttons (no multi-select) acceptable, or is
   multi-select required (pushing us toward the snippet approach)?
3. **Inline docs:** OK to add a `ParentalKey`/migration to enable an `InlinePanel`,
   or keep internal-doc editing in the Django admin for now?

## Test plan

- Filters: date-range narrows the queryset; each filter returns expected rows.
- Exports: standard CSV has the full `ErrataResource` columns; Release-Notes CSV
  has exactly the four renamed columns and the `Release Notes.csv` filename.
- Permissions: Editorial Vendor sees the restricted form; non-Content-Managers
  cannot run status actions, archive, or the Release-Notes export; only superusers
  can delete.
- Per-group `list_display`/`list_filter` differ as specified.
- Inline internal docs render and save (if #5 is in scope).

## Sequencing within Phase 3

1. ViewSet skeleton + filters (incl. date range) + standard CSV export.
2. Release-Notes export (header button).
3. Per-group field/column visibility.
4. Status actions.
5. Inline internal docs (pending decision 3).
6. History (pending decision 1).
7. Remove the Django-admin Errata menu link + the `Errata (Beta)` stub; collapse to
   a single "Errata" entry and slot it into the reorganized menu.
