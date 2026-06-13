# PostHog Experiment Toolkit + Nav Experiment — Implementation Plan (os-webview)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **This plan is executed in the `~/Developer/os-webview` repo**, not openstax-cms. It lives here because that's where the spec lives.
>
> **Commit convention:** the agent prepares the staged diff + message; **Michael runs the actual `git commit`.**

**Goal:** Add a tiny, safe toolkit over the already-loaded `window.posthog` (no init, no new dependency) and use it to ship the CORE-2247 nav experiment: an A/B test of the "Products" dropdown label and a percentage rollout of a top-level K12 menu item.

**Architecture:** PostHog is already loaded and identified by GTM. The frontend only *reads* feature flags and renders variants. A `~/helpers/posthog.ts` module exposes `getExperimentVariant`, `captureEvent`, and a `useExperiment` hook, all hard no-ops when `window.posthog` is absent (pre-consent). Variant decisions are isolated in small pure helpers for easy testing, then wired into `main-menu.tsx`.

**Tech Stack:** Preact (aliased as React), TypeScript (strict), Jest 27 + `@testing-library/preact`.

**Spec:** `docs/posthog-experiments-measurement.md` (in the openstax-cms repo).

**Test command:** `yarn test` (Jest, runs `./test/src`). Single file: `yarn test path/to/test`.

> **Note on the existing `@openstax/experiments` package:** os-webview already has a homegrown `enroll()` helper (used in `give-before-pdf.tsx`). That is **not** PostHog and does not report to PostHog's experiment stats. This toolkit is deliberately separate and PostHog-flag-based. Do not route the nav experiment through `enroll()`.

---

### Task 1: Create the PostHog toolkit (`~/helpers/posthog.ts`) (TDD)

**Files:**
- Create: `src/app/helpers/posthog.ts`
- Test: `test/src/helpers/posthog.test.tsx`

- [ ] **Step 1: Write the failing tests**

Create `test/src/helpers/posthog.test.tsx`:

```tsx
import React from 'react';
import {render, screen, act} from '@testing-library/preact';
import {
    getExperimentVariant,
    captureEvent,
    useExperiment
} from '~/helpers/posthog';

type FakePostHog = {
    getFeatureFlag: jest.Mock;
    onFeatureFlags: jest.Mock;
    capture: jest.Mock;
};

function installPostHog(overrides: Partial<FakePostHog> = {}) {
    const ph: FakePostHog = {
        getFeatureFlag: jest.fn(),
        onFeatureFlags: jest.fn(),
        capture: jest.fn(),
        ...overrides
    };
    (window as unknown as {posthog?: FakePostHog}).posthog = ph;
    return ph;
}

afterEach(() => {
    delete (window as unknown as {posthog?: unknown}).posthog;
});

describe('posthog helper', () => {
    it('getExperimentVariant returns undefined when posthog is absent', () => {
        expect(getExperimentVariant('nav-products-label')).toBeUndefined();
    });

    it('getExperimentVariant reads the flag', () => {
        installPostHog({getFeatureFlag: jest.fn().mockReturnValue('tools')});
        expect(getExperimentVariant('nav-products-label')).toBe('tools');
    });

    it('captureEvent no-ops without posthog', () => {
        expect(() => captureEvent('thing_clicked')).not.toThrow();
    });

    it('captureEvent forwards to posthog', () => {
        const ph = installPostHog();
        captureEvent('thing_clicked', {a: 1});
        expect(ph.capture).toHaveBeenCalledWith('thing_clicked', {a: 1});
    });

    it('useExperiment returns control then updates when flags resolve', async () => {
        const ph = installPostHog({
            getFeatureFlag: jest
                .fn()
                .mockReturnValueOnce(undefined) // initial read
                .mockReturnValue('tools') // after flags load
        });

        function Probe() {
            const variant = useExperiment('nav-products-label');
            return <span>{String(variant)}</span>;
        }

        render(<Probe />);
        screen.getByText('undefined');

        // simulate PostHog finishing flag load
        const cb = ph.onFeatureFlags.mock.calls[0][0] as () => void;
        act(() => cb());
        await screen.findByText('tools');
    });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `yarn test test/src/helpers/posthog.test.tsx`
Expected: FAIL — cannot resolve `~/helpers/posthog`.

- [ ] **Step 3: Implement the toolkit**

Create `src/app/helpers/posthog.ts`:

```ts
import React from 'react';

export type FlagValue = string | boolean | undefined;

type PostHogClient = {
    getFeatureFlag: (key: string) => FlagValue;
    onFeatureFlags: (cb: () => void) => void;
    capture: (event: string, properties?: Record<string, unknown>) => void;
};

/** PostHog is loaded by GTM; it may not be present yet (pre-consent). */
function getPostHog(): PostHogClient | undefined {
    return (window as unknown as {posthog?: PostHogClient}).posthog;
}

/** Read an experiment/feature-flag variant. Reading it auto-fires the
 *  `$feature_flag_called` exposure event in PostHog. */
export function getExperimentVariant(flagKey: string): FlagValue {
    return getPostHog()?.getFeatureFlag(flagKey);
}

/** Fire a goal/auxiliary event. Safe no-op when PostHog is absent. */
export function captureEvent(event: string, properties?: Record<string, unknown>) {
    getPostHog()?.capture(event, properties);
}

/** Hook form: returns the variant, re-rendering once PostHog's flags resolve. */
export function useExperiment(flagKey: string): FlagValue {
    const [variant, setVariant] = React.useState<FlagValue>(() =>
        getExperimentVariant(flagKey)
    );

    React.useEffect(() => {
        const ph = getPostHog();
        if (!ph) {
            return;
        }
        ph.onFeatureFlags(() => setVariant(ph.getFeatureFlag(flagKey)));
    }, [flagKey]);

    return variant;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `yarn test test/src/helpers/posthog.test.tsx`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit** — stage `src/app/helpers/posthog.ts`, `test/src/helpers/posthog.test.tsx`; message: `feat: add PostHog experiment toolkit (read flags, capture events)`

---

### Task 2: Nav A/B — "Products" vs "Tools" dropdown label (TDD)

**Files:**
- Create: `src/app/layouts/default/header/menus/main-menu/nav-experiments.ts` (pure variant logic + flag-key constants)
- Test: `test/src/layouts/default/header/nav-experiments.test.ts`
- Modify: `src/app/layouts/default/header/menus/main-menu/main-menu.tsx`

> **CONFIRM before shipping:** the exact current label of the dropdown to relabel. Test fixtures show CMS dropdowns named like "Technology" / "What we do" — the production `oxmenus` label for the target dropdown must be confirmed and set as `PRODUCTS_DROPDOWN_LABEL`. The logic below relabels only that dropdown.

- [ ] **Step 1: Write the failing tests**

Create `test/src/layouts/default/header/nav-experiments.test.ts`:

```ts
import {
    PRODUCTS_DROPDOWN_LABEL,
    productsDropdownLabel
} from '~/layouts/default/header/menus/main-menu/nav-experiments';

describe('productsDropdownLabel', () => {
    it('leaves non-target dropdowns unchanged', () => {
        expect(productsDropdownLabel('Subjects', 'tools')).toBe('Subjects');
    });

    it('keeps the control label when variant is control/undefined', () => {
        expect(productsDropdownLabel(PRODUCTS_DROPDOWN_LABEL, undefined)).toBe(
            PRODUCTS_DROPDOWN_LABEL
        );
        expect(productsDropdownLabel(PRODUCTS_DROPDOWN_LABEL, 'products')).toBe(
            PRODUCTS_DROPDOWN_LABEL
        );
    });

    it('swaps to "Tools" for the target dropdown in the tools variant', () => {
        expect(productsDropdownLabel(PRODUCTS_DROPDOWN_LABEL, 'tools')).toBe('Tools');
    });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `yarn test test/src/layouts/default/header/nav-experiments.test.ts`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the pure logic + constants**

Create `src/app/layouts/default/header/menus/main-menu/nav-experiments.ts`:

```ts
import type {FlagValue} from '~/helpers/posthog';

/** PostHog flag keys for the nav experiment (CORE-2247). */
export const NAV_PRODUCTS_LABEL_FLAG = 'nav-products-label';
export const NAV_K12_ITEM_FLAG = 'nav-k12-item';

/** The current CMS label of the dropdown under A/B test. CONFIRM against the
 *  production `oxmenus` data before shipping. */
export const PRODUCTS_DROPDOWN_LABEL = 'Products';
const TOOLS_LABEL = 'Tools';

/** Returns the label to render for a CMS dropdown given the A/B variant. */
export function productsDropdownLabel(name: string, variant: FlagValue): string {
    if (name === PRODUCTS_DROPDOWN_LABEL && variant === 'tools') {
        return TOOLS_LABEL;
    }
    return name;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `yarn test test/src/layouts/default/header/nav-experiments.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Wire into `main-menu.tsx`**

In `src/app/layouts/default/header/menus/main-menu/main-menu.tsx`:

Add imports near the top:

```tsx
import {useExperiment} from '~/helpers/posthog';
import {
    NAV_PRODUCTS_LABEL_FLAG,
    productsDropdownLabel
} from './nav-experiments';
```

Replace the dropdown branch of `DropdownOrMenuItem` so the label runs through the experiment helper. The current function returns `<Dropdown label={item.name!} …>`; change that branch to:

```tsx
function DropdownOrMenuItem({item}: {item: MenuItemData}) {
    const productsVariant = useExperiment(NAV_PRODUCTS_LABEL_FLAG);

    if (!('name' in item) && !('label' in item)) {
        return null;
    }
    if ('menu' in item) {
        const label = productsDropdownLabel(item.name!, productsVariant);
        return (
            <Dropdown label={label} navAnalytics={`Main Menu (${item.name})`}>
                <MenusFromStructure structure={item.menu} />
            </Dropdown>
        );
    }

    return <MenuItem label={item.label} url={item.partial_url} />;
}
```

(Keep `navAnalytics` keyed off the original `item.name` so analytics segmentation stays stable across variants — exposure is tracked by the PostHog flag, not the label.)

- [ ] **Step 6: Run the focused suite to confirm nothing broke**

Run: `yarn test test/src/layouts/default/header`
Expected: PASS (existing nav tests + new ones).

- [ ] **Step 7: Commit** — stage `nav-experiments.ts`, its test, and `main-menu.tsx`; message: `feat: A/B test the Products/Tools nav dropdown label via PostHog`

---

### Task 3: Nav percentage rollout — top-level K12 menu item (TDD)

**Files:**
- Modify: `src/app/layouts/default/header/menus/main-menu/main-menu.tsx`
- Test: `test/src/layouts/default/header/main-menu-k12.test.tsx`

Behavior: when `nav-k12-item` is on, render `K12MenuItem` as a **top-level** nav item (in `MainMenuItems`) and **remove** the in-dropdown K12 item from `SubjectsMenu`. When off (control), behave exactly as today (K12 only inside the Subjects dropdown).

- [ ] **Step 1: Write the failing test**

Create `test/src/layouts/default/header/main-menu-k12.test.tsx`:

```tsx
import React from 'react';
import {render, screen} from '@testing-library/preact';
import {MemoryRouter} from 'react-router-dom';
import {MainMenuItems} from '~/layouts/default/header/menus/main-menu/main-menu';
import ShellContextProvider from '../../../../helpers/shell-context';

type FakePostHog = {
    getFeatureFlag: jest.Mock;
    onFeatureFlags: jest.Mock;
    capture: jest.Mock;
};

function installFlag(value: boolean) {
    const ph: FakePostHog = {
        getFeatureFlag: jest.fn().mockReturnValue(value),
        onFeatureFlags: jest.fn(),
        capture: jest.fn()
    };
    (window as unknown as {posthog?: FakePostHog}).posthog = ph;
}

afterEach(() => {
    delete (window as unknown as {posthog?: unknown}).posthog;
});

function renderMenu() {
    return render(
        <MemoryRouter>
            <ShellContextProvider>
                <ul>
                    <MainMenuItems />
                </ul>
            </ShellContextProvider>
        </MemoryRouter>
    );
}

describe('K12 nav rollout', () => {
    it('renders a top-level K12 item when the flag is on', async () => {
        installFlag(true);
        renderMenu();
        const links = await screen.findAllByRole('link', {name: /K12 Teachers/i});
        // top-level item points at /k12
        expect(links.some((a) => a.getAttribute('href') === '/k12')).toBe(true);
    });

    it('renders no top-level K12 item when the flag is off', async () => {
        installFlag(false);
        const {container} = renderMenu();
        // The top-level item lives directly under the menu's first-level <li>s,
        // not nested in a dropdown. Assert it is not a direct child link.
        const topLevel = container.querySelectorAll(':scope > ul > li > a[href="/k12"]');
        expect(topLevel.length).toBe(0);
    });
});
```

(If `test/helpers/shell-context.js` is missing the subject-category provider needed by `SubjectsMenu`, extend it — see the Explore notes; it already wraps `SubjectCategoryContextProvider`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `yarn test test/src/layouts/default/header/main-menu-k12.test.tsx`
Expected: FAIL — no top-level K12 link in the "on" case (current code only renders K12 inside the Subjects dropdown).

- [ ] **Step 3: Implement the rollout**

In `main-menu.tsx`, add the flag import (extend the existing `nav-experiments` import):

```tsx
import {
    NAV_PRODUCTS_LABEL_FLAG,
    NAV_K12_ITEM_FLAG,
    productsDropdownLabel
} from './nav-experiments';
```

In `SubjectsMenu`, gate the in-dropdown K12 item. Replace the existing K12 block:

```tsx
            {language === 'en' ? (
                <React.Fragment>
                    <hr />
                    <K12MenuItem />
                </React.Fragment>
            ) : null}
```

with a version that hides it when the rollout is on:

```tsx
            {language === 'en' && !k12TopLevel ? (
                <React.Fragment>
                    <hr />
                    <K12MenuItem />
                </React.Fragment>
            ) : null}
```

and read the flag at the top of `SubjectsMenu` (after its existing hooks):

```tsx
    const k12TopLevel = Boolean(useExperiment(NAV_K12_ITEM_FLAG));
```

Then update `MainMenuItems` to render the top-level item when on:

```tsx
export function MainMenuItems() {
    const k12TopLevel = Boolean(useExperiment(NAV_K12_ITEM_FLAG));
    return (
        <React.Fragment>
            <SubjectsMenu />
            <MenusFromCMS />
            {k12TopLevel ? <K12MenuItem /> : null}
            <li className="give-button-item">
                <GiveButton />
            </li>
            <LoginMenu />
        </React.Fragment>
    );
}
```

(Add `useExperiment` to the import from `~/helpers/posthog` if Task 2 didn't already.)

- [ ] **Step 4: Run test to verify it passes**

Run: `yarn test test/src/layouts/default/header/main-menu-k12.test.tsx`
Expected: PASS (2 tests).

- [ ] **Step 5: Run the header suite + typecheck**

Run: `yarn test test/src/layouts/default/header` then `yarn tsc --noEmit` (or the project's typecheck script).
Expected: tests PASS; no new TS errors.

- [ ] **Step 6: Commit** — stage `main-menu.tsx`, `main-menu-k12.test.tsx`; message: `feat: percentage-rollout a top-level K12 nav item via PostHog`

---

## Full-suite check (after all tasks)

Run: `yarn test`
Expected: green (with coverage). Investigate any pre-existing failures separately from this work.

## Verify-during-implementation (from the spec)

- **`PRODUCTS_DROPDOWN_LABEL`:** confirm the exact production `oxmenus` label of the
  dropdown being A/B tested and update the constant. The A/B does nothing until it
  matches a real dropdown name.
- **Identity:** none needed here — GTM already calls `posthog.identify` on the UUID.
  Confirm this in the live GTM container before assuming exposure events are
  attributed.
- **Goal metric:** ensure the dropdown's nav click + downstream
  `book_engagement_clicked` are the goals configured in PostHog's Experiments UI
  (config lives in PostHog, not code).
