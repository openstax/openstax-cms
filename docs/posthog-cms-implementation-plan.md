# PostHog Server-Side Capture + CMS Guide — Implementation Plan (openstax-cms)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Commit convention for THIS repo:** the agent prepares the staged diff + a commit message; **Michael runs the actual `git commit`.** Where a step says "Commit", stage the files and hand over the message — do not run `git commit` yourself.

**Goal:** Add reliable, consent-independent server-side PostHog capture for Django-processed form submissions (errata, donation thank-you), plus a Wagtail admin "Experiments & Measurement" guide and a change-and-measure runbook.

**Architecture:** A single tiny `shared/analytics.py` helper wraps the PostHog Python SDK and **no-ops unless `POSTHOG_API_KEY` is set** (so local/CI are untouched). Existing `post_save` signals fire `capture()` on create. A Wagtail admin view renders a static guide page of links. No model/API contract changes beyond an optional account-id passthrough already present on errata.

**Tech Stack:** Django 5.2, Wagtail 7.4, DRF, `posthog` Python SDK, `unittest.mock`.

**Spec:** `docs/posthog-experiments-measurement.md`

**Test command:** `python manage.py test shared errata donations global_settings --settings=openstax.settings.test` (run inside the `openstax-cms` virtualenv: `workon openstax-cms`).

---

### Task 1: Add the `posthog` dependency and settings

**Files:**
- Modify: `requirements/base.txt`
- Modify: `openstax/settings/base.py` (after the Sentry block, ~line 673)

- [ ] **Step 1: Add the dependency**

In `requirements/base.txt`, add a line (match the existing range-pin style):

```
posthog>=3.7,<4.0
```

- [ ] **Step 2: Install it**

Run: `workon openstax-cms && pip install -r requirements/base.txt`
Expected: `posthog` installs without conflicts.

- [ ] **Step 3: Add settings**

In `openstax/settings/base.py`, immediately after the Sentry `sentry_sdk.init(...)` block, add:

```python
# --- PostHog (server-side capture) -----------------------------------------
# Disabled (no-op) whenever POSTHOG_API_KEY is unset — e.g. local dev and CI.
POSTHOG_API_KEY = os.getenv('POSTHOG_API_KEY')
POSTHOG_HOST = os.getenv('POSTHOG_HOST', 'https://z.openstax.org')
```

- [ ] **Step 4: Verify settings import cleanly**

Run: `python manage.py shell --settings=openstax.settings.test -c "from django.conf import settings; print(settings.POSTHOG_HOST)"`
Expected: prints `https://z.openstax.org`, no errors.

- [ ] **Step 5: Commit** — stage `requirements/base.txt` and `openstax/settings/base.py`; hand over message: `chore: add posthog SDK dependency and settings`

---

### Task 2: Create the `shared/analytics.py` capture helper (TDD)

**Files:**
- Create: `shared/analytics.py`
- Test: `shared/test_analytics.py`

- [ ] **Step 1: Write the failing tests**

Create `shared/test_analytics.py`:

```python
from unittest import mock

from django.test import TestCase, override_settings

from shared import analytics


class AnalyticsCaptureTest(TestCase):
    def setUp(self):
        analytics._client = None  # reset memoized client between tests

    @override_settings(POSTHOG_API_KEY=None)
    @mock.patch('shared.analytics.Posthog')
    def test_capture_is_noop_when_unconfigured(self, mock_posthog):
        analytics.capture('errata_submitted', distinct_id='uuid-1')
        mock_posthog.assert_not_called()

    @override_settings(POSTHOG_API_KEY='phc_test', POSTHOG_HOST='https://z.openstax.org')
    @mock.patch('shared.analytics.Posthog')
    def test_capture_sends_identified_event(self, mock_posthog):
        client = mock_posthog.return_value
        analytics.capture(
            'errata_submitted',
            distinct_id='uuid-1',
            properties={'form_type': 'errata'},
        )
        client.capture.assert_called_once()
        kwargs = client.capture.call_args.kwargs
        self.assertEqual(kwargs['distinct_id'], 'uuid-1')
        self.assertEqual(kwargs['event'], 'errata_submitted')
        self.assertEqual(kwargs['properties']['form_type'], 'errata')
        self.assertEqual(kwargs['properties']['source'], 'server')

    @override_settings(POSTHOG_API_KEY='phc_test')
    @mock.patch('shared.analytics.Posthog')
    def test_capture_anonymous_disables_person_profile(self, mock_posthog):
        client = mock_posthog.return_value
        analytics.capture('thank_you_note_submitted')
        kwargs = client.capture.call_args.kwargs
        self.assertTrue(kwargs['properties']['$process_person_profile'] is False)
        self.assertTrue(kwargs['distinct_id'])  # a generated id, not empty

    @override_settings(POSTHOG_API_KEY='phc_test')
    @mock.patch('shared.analytics.Posthog')
    def test_capture_swallows_sdk_errors(self, mock_posthog):
        mock_posthog.return_value.capture.side_effect = RuntimeError('boom')
        # must not raise
        analytics.capture('errata_submitted', distinct_id='uuid-1')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python manage.py test shared.test_analytics --settings=openstax.settings.test`
Expected: FAIL — `AttributeError: module 'shared.analytics' has no attribute 'capture'` (module doesn't exist yet).

- [ ] **Step 3: Implement the helper**

Create `shared/analytics.py`:

```python
"""Server-side PostHog capture.

Fire-and-forget. A hard no-op unless ``settings.POSTHOG_API_KEY`` is set, so
local development and CI are unaffected. Never lets analytics break a request.
"""
import logging
import uuid

from django.conf import settings
from posthog import Posthog

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if not getattr(settings, 'POSTHOG_API_KEY', None):
        return None
    if _client is None:
        _client = Posthog(
            settings.POSTHOG_API_KEY,
            host=getattr(settings, 'POSTHOG_HOST', 'https://z.openstax.org'),
        )
    return _client


def capture(event, distinct_id=None, properties=None):
    """Capture a server-side event.

    ``distinct_id`` should be the accounts UUID when known, so the event joins
    the visitor's existing PostHog identity (and the Salesforce pipeline).
    When unknown, the event is sent anonymously with no person profile.
    """
    client = _get_client()
    if client is None:
        return

    props = dict(properties or {})
    props.setdefault('source', 'server')

    if distinct_id:
        did = str(distinct_id)
    else:
        did = str(uuid.uuid4())
        props['$process_person_profile'] = False

    try:
        client.capture(distinct_id=did, event=event, properties=props)
    except Exception:  # noqa: BLE001 — analytics must never break a request
        logger.exception('PostHog capture failed for event %s', event)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test shared.test_analytics --settings=openstax.settings.test`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit** — stage `shared/analytics.py`, `shared/test_analytics.py`; message: `feat: add server-side PostHog capture helper`

---

### Task 3: Capture `errata_submitted` on errata creation (TDD)

**Files:**
- Modify: `errata/models.py` (imports near top; new receiver after the existing `send_status_update_email` receiver at line 309)
- Test: `errata/tests.py` (append)

Note: errata's `submitted_by_account_id` is an account **ID**, not a UUID. We resolve the UUID via the already-imported `get_user_info()` (best-effort), and fall back to an anonymous event if it can't be resolved. We test the receiver directly (no ORM/Book scaffolding needed).

- [ ] **Step 1: Write the failing tests**

Append to `errata/tests.py`:

```python
from unittest import mock

from django.test import TestCase as DjangoTestCase


class ErrataPostHogCaptureTest(DjangoTestCase):
    def _instance(self, account_id=None):
        return mock.Mock(
            submitted_by_account_id=account_id,
            book_id=1,
            book=mock.Mock(title='Biology 2e'),
            error_type='Typo',
        )

    @mock.patch('errata.models.posthog_capture')
    def test_no_capture_on_update(self, mock_capture):
        from errata.models import capture_errata_submitted
        capture_errata_submitted(sender=None, instance=self._instance(), created=False)
        mock_capture.assert_not_called()

    @mock.patch('errata.models.get_user_info', return_value={'uuid': 'uuid-9', 'email': 'a@b.co'})
    @mock.patch('errata.models.posthog_capture')
    def test_capture_identified_on_create(self, mock_capture, _mock_user):
        from errata.models import capture_errata_submitted
        capture_errata_submitted(sender=None, instance=self._instance(account_id=42), created=True)
        mock_capture.assert_called_once()
        kwargs = mock_capture.call_args.kwargs
        self.assertEqual(kwargs['distinct_id'], 'uuid-9')
        self.assertEqual(kwargs['properties']['form_type'], 'errata')
        self.assertEqual(kwargs['properties']['book'], 'Biology 2e')

    @mock.patch('errata.models.posthog_capture')
    def test_capture_anonymous_when_no_account(self, mock_capture):
        from errata.models import capture_errata_submitted
        capture_errata_submitted(sender=None, instance=self._instance(account_id=None), created=True)
        kwargs = mock_capture.call_args.kwargs
        self.assertIsNone(kwargs['distinct_id'])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python manage.py test errata.tests.ErrataPostHogCaptureTest --settings=openstax.settings.test`
Expected: FAIL — `ImportError: cannot import name 'capture_errata_submitted'`.

- [ ] **Step 3: Add the import and receiver**

In `errata/models.py`, near the other imports (after `from openstax_accounts.functions import get_user_info`), add:

```python
from shared.analytics import capture as posthog_capture
```

After the existing `@receiver(post_save, sender=Errata, dispatch_uid="send_status_update_email")` function (ends near line 410), add:

```python
@receiver(post_save, sender=Errata, dispatch_uid="errata_posthog_capture")
def capture_errata_submitted(sender, instance, created, **kwargs):
    if not created:
        return
    distinct_id = None
    if instance.submitted_by_account_id:
        try:
            user = get_user_info(instance.submitted_by_account_id)
            distinct_id = user.get('uuid') if isinstance(user, dict) else None
        except Exception:  # noqa: BLE001 — never block a submission on lookup
            distinct_id = None
    posthog_capture(
        'errata_submitted',
        distinct_id=distinct_id,
        properties={
            'form_type': 'errata',
            'book': instance.book.title if instance.book_id else None,
            'error_type': instance.error_type,
            'account_id': instance.submitted_by_account_id,
        },
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test errata.tests.ErrataPostHogCaptureTest --settings=openstax.settings.test`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit** — stage `errata/models.py`, `errata/tests.py`; message: `feat: capture errata_submitted server-side in PostHog`

---

### Task 4: Capture `thank_you_note_submitted` on donation thank-you creation (TDD)

**Files:**
- Modify: `donations/signals.py` (import `ThankYouNote`; add receiver)
- Test: `donations/tests.py` (append)

`ThankYouNote` carries no account identity, so this event is anonymous. `signals.py` is already wired (it has active receivers), so a new `post_save` receiver fires automatically. We test through the real endpoint (`ThankYouNote.objects.create()` in the view triggers the signal).

- [ ] **Step 1: Write the failing test**

Append to `donations/tests.py`:

```python
from unittest import mock


class ThankYouNotePostHogTest(APITestCase, TestCase):
    @mock.patch('donations.signals.posthog_capture')
    def test_thank_you_note_post_fires_posthog_event(self, mock_capture):
        data = {
            "thank_you_note": "Thanks OpenStax!",
            "last_name": "Drew",
            "first_name": "Jessica",
            "school": "Rice University",
            "consent_to_share_or_contact": "True",
            "contact_email_address": "jess@example.com",
            "source": "PDF download",
        }
        response = self.client.post(
            '/apps/cms/api/donations/thankyounote/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_capture.assert_called_once()
        self.assertEqual(mock_capture.call_args.args[0], 'thank_you_note_submitted')
        self.assertEqual(
            mock_capture.call_args.kwargs['properties']['form_type'],
            'donation_thank_you',
        )
```

(`APITestCase`, `TestCase`, and `status` are already imported at the top of `donations/tests.py`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test donations.tests.ThankYouNotePostHogTest --settings=openstax.settings.test`
Expected: FAIL — `AttributeError: <module 'donations.signals'> does not have the attribute 'posthog_capture'`.

- [ ] **Step 3: Add the import and receiver**

In `donations/signals.py`, update the model import and add the helper import + receiver:

```python
from .models import DonationPopup, Fundraiser, SiteBanner, ThankYouNote
from shared.analytics import capture as posthog_capture


@receiver(post_save, sender=ThankYouNote)
def capture_thank_you_note(sender, instance, created, **kwargs):
    if not created:
        return
    posthog_capture(
        'thank_you_note_submitted',
        properties={'form_type': 'donation_thank_you'},
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python manage.py test donations.tests.ThankYouNotePostHogTest --settings=openstax.settings.test`
Expected: PASS.

- [ ] **Step 5: Commit** — stage `donations/signals.py`, `donations/tests.py`; message: `feat: capture donation thank-you submissions server-side in PostHog`

---

### Task 5: Wagtail admin "Experiments & Measurement" guide page (TDD)

**Files:**
- Create: `global_settings/views.py` (if it doesn't exist; otherwise append)
- Create: `global_settings/templates/experiments_guide.html`
- Modify: `global_settings/wagtail_hooks.py` (add admin URL + settings menu item)
- Test: `global_settings/tests.py` (append; create if absent)

- [ ] **Step 1: Write the failing test**

Append to `global_settings/tests.py` (create the file with this content if it doesn't exist):

```python
from django.urls import reverse

from wagtail.test.utils import WagtailTestUtils
from django.test import TestCase


class ExperimentsGuideTest(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()  # creates and logs in a superuser

    def test_guide_page_renders_with_links(self):
        response = self.client.get(reverse('experiments_guide'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Experiments &amp; Measurement')
        self.assertContains(response, 'us.posthog.com')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test global_settings.tests.ExperimentsGuideTest --settings=openstax.settings.test`
Expected: FAIL — `NoReverseMatch: Reverse for 'experiments_guide' not found`.

- [ ] **Step 3: Add the view**

In `global_settings/views.py` add (create the file if needed, with `from django.shortcuts import render` at top):

```python
def experiments_guide(request):
    return render(request, 'experiments_guide.html', {
        'posthog_project_url': 'https://us.posthog.com/project/105101',
        'framework_doc': '/docs/posthog-experiments-measurement.md',
        'runbook_doc': '/docs/posthog-experiments-runbook.md',
    })
```

- [ ] **Step 4: Add the template**

Create `global_settings/templates/experiments_guide.html`:

```html
{% extends "wagtailadmin/base.html" %}
{% block titletag %}Experiments & Measurement{% endblock %}
{% block content %}
  {% include "wagtailadmin/shared/header.html" with title="Experiments & Measurement" icon="bulb" %}
  <div class="nice-padding">
    <p>Run measurable website changes with PostHog feature flags &amp; experiments.
       A/B test a change, ramp it with a percentage rollout, and read the result.</p>
    <h2>Where to go</h2>
    <ul>
      <li><a href="{{ posthog_project_url }}" target="_blank" rel="noopener">PostHog project (create flags &amp; experiments)</a></li>
      <li><a href="{{ framework_doc }}" target="_blank" rel="noopener">Framework overview</a></li>
      <li><a href="{{ runbook_doc }}" target="_blank" rel="noopener">Change-and-measure runbook (step by step)</a></li>
    </ul>
    <h2>The short version</h2>
    <ol>
      <li>Create a feature flag in PostHog (boolean for a rollout, multivariate for an A/B).</li>
      <li>Name it surface-first, kebab-case — e.g. <code>nav-products-label</code>, <code>nav-k12-item</code>.</li>
      <li>Pick a goal metric — an event already flowing (a nav click, <code>book_engagement_clicked</code>, a form submit).</li>
      <li>Ramp a rollout 10% → 25% → 100% in PostHog. No code change.</li>
      <li>Read lift &amp; significance in PostHog's Experiments tab.</li>
    </ol>
  </div>
{% endblock %}
```

- [ ] **Step 5: Register the URL and menu item**

In `global_settings/wagtail_hooks.py`, add at the top (with the other imports): `from django.urls import path` (already present) and `from global_settings import views`. Then add:

```python
@hooks.register('register_admin_urls')
def register_experiments_guide_url():
    return [path('experiments/', views.experiments_guide, name='experiments_guide')]


@hooks.register('register_settings_menu_item')
def register_experiments_menu_item():
    return MenuItem(
        'Experiments & Measurement',
        reverse('experiments_guide'),
        icon_name='bulb',
        order=9000,
    )
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python manage.py test global_settings.tests.ExperimentsGuideTest --settings=openstax.settings.test`
Expected: PASS.

- [ ] **Step 7: Commit** — stage `global_settings/views.py`, `global_settings/templates/experiments_guide.html`, `global_settings/wagtail_hooks.py`, `global_settings/tests.py`; message: `feat: add Experiments & Measurement guide to Wagtail admin`

---

### Task 6: Write the change-and-measure runbook (the CORE-2246 exemplar)

**Files:**
- Create: `docs/posthog-experiments-runbook.md`

No test — documentation. This is the exemplar other contributors copy.

- [ ] **Step 1: Write the runbook**

Create `docs/posthog-experiments-runbook.md` with these sections (use the nav experiment as the worked example so it's concrete):

```markdown
# How to change something and measure it (PostHog)

The exemplar for CORE-2246. Worked example: the navigation A/B + K12 rollout (CORE-2247).

## 1. Decide the change and the goal
- What are you changing? (e.g. relabel the "Products" dropdown to "Tools".)
- What does success look like, as an event already flowing? (e.g. more clicks into
  the affected dropdown, or downstream `book_engagement_clicked`.)

## 2. Create the feature flag in PostHog
- A/B test → multivariate flag (e.g. `nav-products-label` with variants
  `products` / `tools`).
- Gradual rollout → boolean flag (e.g. `nav-k12-item`) at 10%.
- Naming: surface-first, kebab-case.

## 3. Wire the frontend (os-webview)
- Read the flag with `useExperiment('<flag-key>')` from `~/helpers/posthog`.
- Render the variant. Reading the flag auto-fires the `$feature_flag_called`
  exposure event — that's your denominator, no extra code.

## 4. Create the experiment / read results in PostHog
- In PostHog → Experiments, point the experiment at the flag and the goal metric.
- For a plain rollout, watch the goal metric per flag value in an insight.

## 5. Ramp and decide
- Move the rollout 10% → 25% → 100% in PostHog (no deploy).
- When significance is reached, ship the winner as the default and retire the flag.

## Conventions
- Flags: kebab-case, surface-prefixed (`nav-products-label`).
- Events: snake_case verbs; server-side events carry `source: 'server'`.
- Identity: the accounts UUID is the distinct_id (handled client-side by GTM,
  mirrored server-side when available).

## Server-side capture (this repo)
- Use `shared.analytics.capture(event, distinct_id=<uuid or None>, properties={...})`.
- It no-ops unless `POSTHOG_API_KEY` is set. Already wired into errata and
  donation thank-you submissions.
```

- [ ] **Step 2: Commit** — stage `docs/posthog-experiments-runbook.md`; message: `docs: add change-and-measure runbook`

---

## Full-suite check (after all tasks)

Run: `python manage.py test shared errata donations global_settings --settings=openstax.settings.test`
Expected: all green. Add `--keepdb` to reuse the test DB on reruns.

## Verify-during-implementation (from the spec)

- **`get_user_info()` UUID key:** confirm the returned dict actually has a `uuid`
  key (Task 3 defensively reads `user.get('uuid')` and falls back to anonymous —
  but verify so identified errata events actually join). If the key differs, adjust
  the receiver.
- **Donation identity:** if you later want donation thank-you events attributed,
  the frontend must pass the UUID in the POST payload (out of scope here).
