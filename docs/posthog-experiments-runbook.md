# How to change something and measure it (PostHog)

The exemplar for [CORE-2246](https://openstax.atlassian.net/browse/CORE-2246).
Worked example: the navigation A/B + K12 rollout ([CORE-2247](https://openstax.atlassian.net/browse/CORE-2247)).

PostHog already runs on openstax.org (loaded via Google Tag Manager) and already
identifies visitors by their accounts UUID, so events join the same person and
flow on to Salesforce. You don't set any of that up — you just create a flag,
read it in the frontend, and read the result.

## 1. Decide the change and the goal

- **What are you changing?** (e.g. relabel the "Products" dropdown to "Tools".)
- **What does success look like, as an event that already flows?** (e.g. more
  clicks into the affected dropdown, or downstream `book_engagement_clicked`.)
  If no event captures your goal yet, add one with `captureEvent()` in os-webview
  (or `shared.analytics.capture()` server-side) before you start.

## 2. Create the feature flag in PostHog

- **A/B test** → a **multivariate** flag (e.g. `nav-products-label` with variants
  `products` / `tools`).
- **Gradual rollout** → a **boolean** flag (e.g. `nav-k12-item`) starting at 10%.
- **Naming:** surface-first, kebab-case — `nav-products-label`, `nav-k12-item`.

## 3. Wire the frontend (os-webview)

- Read the flag with `useExperiment('<flag-key>')` from `~/helpers/posthog`.
- Render the variant. **Reading the flag auto-fires the `$feature_flag_called`
  exposure event** — that's your experiment denominator, no extra code.
- Keep variants visually compatible to avoid flicker (a label swap is in-place; an
  added item just appears).

## 4. Create the experiment / read results in PostHog

- In PostHog → **Experiments**, point the experiment at the flag and the goal
  metric. PostHog computes lift and statistical significance per variant.
- For a plain rollout (no A/B), watch the goal metric broken down by flag value in
  an insight.

## 5. Ramp and decide

- Move the rollout 10% → 25% → 100% in PostHog (no deploy).
- When significance is reached, ship the winning variant as the default in code and
  retire the flag.

## Conventions

- **Flags:** kebab-case, surface-prefixed (`nav-products-label`).
- **Events:** snake_case verbs (`book_engagement_clicked`); server-side events
  carry `source: 'server'` and a `form_type` property.
- **Identity:** the accounts UUID is the `distinct_id` (handled client-side by GTM,
  mirrored server-side when available). No net-new PII beyond what already flows.

## Server-side capture (openstax-cms)

For events the Django backend processes (form submissions like errata and donation
thank-you notes), capture server-side so they're counted regardless of cookie
consent or ad-blockers:

```python
from shared.analytics import capture

capture(
    'errata_submitted',
    distinct_id=<accounts uuid or None>,
    properties={'form_type': 'errata', 'source': 'server'},
)
```

- It's a **hard no-op unless `POSTHOG_API_KEY` is set**, so local dev and CI are
  unaffected.
- Already wired into errata submissions (`errata/models.py`) and donation
  thank-you notes (`donations/signals.py`).
- **Downloads are not captured server-side** — book PDFs/resources are served as
  direct CDN URLs that never pass through Django. They stay on the existing GTM
  client-side tags (`resource_downloaded`, `book_engagement_clicked`).
