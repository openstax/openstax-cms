# PostHog Experiments & Measurement Framework

**Status:** Design / spec
**Date:** 06/12/2026
**Tickets:** [CORE-2246](https://openstax.atlassian.net/browse/CORE-2246) (measurement & instrumentation framework / exemplar), [CORE-2247](https://openstax.atlassian.net/browse/CORE-2247) (nav revamp — the proving ground)
**Repos:** `openstax-cms` (this repo) and `os-webview` (frontend)

---

## Goal

Make website changes measurable end to end so any contributor can ship a change
and know how to read its impact. PostHog already runs on openstax.org (loaded via
Google Tag Manager) and already feeds the Salesforce data pipeline; the gap is a
documented, repeatable **change-and-measure loop** plus a small reusable way to
run A/B tests and percentage rollouts. The navigation revamp (CORE-2247) is the
first real test case and becomes the exemplar.

## Background / what already exists

- **PostHog is loaded by GTM**, not by an npm package. The init (from the GTM
  Custom HTML tag) is:
  ```js
  posthog.init('phc_bnZwQPxzoC7WnmjFNOUQpcKsaDVg8TwnyoNzbClpIsD', {
      api_host: 'https://z.openstax.org',   // reverse proxy
      ui_host: 'https://us.posthog.com',
      defaults: '2026-01-30',
      person_profiles: 'identified_only',
  })
  ```
  Consequence: the frontend must **use the already-present `window.posthog`** and
  must **not** re-init it.
- **Identity is already handled by GTM** — events arrive identified on the
  accounts **UUID** (with role), so the frontend toolkit does **not** need to call
  `identify`.
- **Events already captured client-side via GTM** include `resource_downloaded`,
  `book_engagement_clicked`, `form_submitted_gtm`, plus PostHog autocapture
  (`Pageview`, `Pageleave`).
- **`person_profiles: 'identified_only'`** means anonymous events do not create
  person profiles — relevant for server-side capture (anonymous calls won't create
  stray profiles).
- **Downloads bypass Django.** Book PDFs are served as direct document URLs
  (`books/models.py` → `get_high_res_pdf_url()` / `build_document_url()`), and the
  frontend links straight to storage/CDN. The CMS is not in the download request
  path, so it cannot capture downloads server-side. Downloads stay on the existing
  GTM client-side tags. (A future redirect-capture view is out of scope — see
  "Future work".)
- **The primary nav is CMS-driven**: `main-menu.tsx` pulls structure from
  `useDataFromSlug('oxmenus')` (the `Menus` model in the `oxmenus` app). K12 today
  lives *inside* the Subjects dropdown as a hardcoded `K12MenuItem`
  ("🍎 For K12 Teachers" → `/k12`), and the `html === 'K12'` category is filtered
  out of the subjects list.

## How PostHog experiments work (reference)

1. **A feature flag is the experiment.** Create the flag in PostHog; it
   deterministically buckets each visitor by `distinct_id` (the UUID), so a person
   always sees the same variant and the split is reportable.
2. **The frontend asks "which variant?"** via `posthog.getFeatureFlag(key)` or
   `posthog.onFeatureFlags(cb)`, and renders accordingly. Reading a flag
   auto-fires the `$feature_flag_called` **exposure** event (the experiment
   denominator) — no extra code.
3. **A goal metric** is an existing event (nav click, `book_engagement_clicked`,
   a form submit). PostHog's Experiments UI computes lift + significance.
4. **Percentage rollout** is the same flag at 10% → 25% → 100% — a dial in
   PostHog, no code change.

So the reusable toolkit is small: read a flag, render a variant, make sure the
goal event fires. Experiment *config* lives in PostHog, owned by whoever runs it.

---

## Scope (V1)

### Component 1 — Client experiment toolkit (`os-webview`)
A small module over the already-loaded `window.posthog` (no init, no new
dependency):
- `getExperimentVariant(flagKey)` and a `useExperiment(flagKey)` Preact hook —
  returns the variant once `onFeatureFlags` resolves; control/`undefined` until
  then.
- `captureEvent(name, props)` — thin wrapper, **safe no-op when `window.posthog`
  is absent** (pre-consent / not loaded) — for any goal event not already covered
  by GTM tags.
- Every call guarded so nothing breaks when PostHog is not present.

### Component 2 — Nav experiment (`os-webview`, the CORE-2247 exemplar)
In `src/app/layouts/default/header/menus/main-menu/main-menu.tsx`:
- **A/B — `nav-products-label`** (multivariate: `products` | `tools`): swaps the
  affected dropdown label in place. Low flicker (text swap).
- **% rollout — `nav-k12-item`** (boolean; ramp 10 → 25 → 100%): when on, render
  `K12MenuItem` as a **top-level** nav item and remove it from the Subjects
  dropdown. Additive on appearance → no flicker.
- **Goals:** existing events — nav click on the affected items and downstream
  `book_engagement_clicked`. Read in PostHog's Experiments UI; no per-experiment
  code.

### Component 3 — Server-side capture (`openstax-cms`)
- Add `posthog` (Python SDK) to requirements.
- A small `analytics` helper that lazy-inits a client from settings
  (`POSTHOG_API_KEY`, `POSTHOG_HOST` → the `z.openstax.org` proxy) and exposes
  `capture(distinct_id, event, properties)`. **No-op when unconfigured** (local /
  test) so it never breaks dev or CI.
- `distinct_id` = the accounts **UUID** when the request carries it (keeps the
  join + Salesforce pipeline intact); anonymous otherwise.
- Wire into **Django-processed submissions only**: errata, donation thank-you, and
  server-side form submits. Each carries `source: 'server'` to distinguish from
  the GTM client events. (Downloads are intentionally excluded — they bypass
  Django.)

### Component 4 — CMS contributor guide + exemplar runbook (`openstax-cms`)
- A Wagtail admin **menu item "Experiments & Measurement"** registered via
  `wagtail_hooks.py` (matching the pattern in
  `global_settings/wagtail_hooks.py`), linking to: the PostHog project, a short
  how-to, and the runbook.
- The **CORE-2246 "change-and-measure" runbook**: how to create a flag/experiment,
  name it, pick a goal metric, ramp a rollout, and read significance — using the
  nav experiment as the worked example. This is the exemplar other contributors
  copy.

---

## Conventions

- **Feature flags:** kebab-case, surface-prefixed — `nav-products-label`,
  `nav-k12-item`.
- **Events:** snake_case verbs, matching existing (`book_engagement_clicked`).
  New server events carry `source: 'server'` and a `form_type` property.
- **Identity:** the accounts UUID as `distinct_id`. Already handled client-side by
  GTM; mirrored server-side when the request carries the UUID. No net-new PII
  beyond what already flows through the existing setup.

## Architecture notes / decisions

- **Do not re-init PostHog** in `os-webview` — use `window.posthog` only.
- **Flicker:** keep variants in place. The label A/B is a text swap; the K12 item
  is additive. Acceptable for a header without flag bootstrapping.
- **Identity in the frontend toolkit:** not needed — GTM already identifies.
  (Verify this assumption during implementation before deciding whether any
  `identify` call is required.)
- **Server-side safety:** the `analytics` helper must be a hard no-op when
  `POSTHOG_API_KEY` is unset, so local dev and the test suite are unaffected.

## Out of scope (V1)

- **Download redirect-capture** (routing downloads through a Django view to capture
  server-side regardless of consent). Tracked as future work.
- Homepage restructure beyond the nav.
- Net-new pages (CCR hub etc., covered by other CORE tickets).

## Future work

- **Download capture reliability:** a `/download/<book>/<type>` Django
  redirect-capture view that fires a server-side PostHog event then 302s to the
  CDN URL — the only way to capture downloads regardless of consent/ad-blockers.
  Changes the API contract and the frontend; deferred until the experiment loop is
  proven.

## Open questions / verify during implementation

1. Confirm GTM already calls `posthog.identify(uuid, …)` (screenshots strongly
   suggest yes) before deciding the frontend needs no `identify`.
2. Confirm which dropdown carries the "Products"/"Tools" label and whether the
   label is sourced from `oxmenus` (CMS) or hardcoded — determines where the A/B
   variant text comes from.
3. Confirm whether errata / donation / form submit code paths reliably receive the
   UUID server-side, or whether the frontend must pass it for attribution.
