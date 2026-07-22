/*
 * Collapses a StreamField block by default when it first enters the editor.
 *
 * Wagtail 7.4 wraps every StreamField block (any type, not just Struct/Stream/
 * ListBlock containers) in the same collapsible "panel" chrome — a
 * `[data-panel]` section with a `[data-panel-toggle]` button. There is no
 * Python-level `collapsed` option for a plain field block (only container
 * blocks respect it), so this drives the existing toggle button directly,
 * once, the same way a person clicking it would.
 *
 * Attached via `data-controller="openstax-collapse-block"` on the field
 * itself (see CollapsedHTMLBlock in pages/shared_blocks.py). Stimulus runs
 * connect() when the element enters the DOM — for the initial page load and
 * for a block freshly added from the block picker — so no MutationObserver
 * or manual re-scan is needed.
 *
 * Fragile to a Wagtail admin UI rewrite: if `[data-panel]`/`[data-panel-toggle]`
 * ever change, this becomes a silent no-op (the guard clauses just return),
 * not a crash.
 *
 * A drag-reorder (or other DOM churn) can disconnect and reconnect this
 * controller without the panel itself being torn down, so a marker on the
 * panel (not the controller instance, which doesn't survive that cycle)
 * remembers that the one-time collapse already ran -- otherwise a block the
 * editor deliberately re-expanded would collapse again on the next reconnect.
 * The marker is set as soon as a toggle is found on first connect, whether
 * or not the panel is expanded yet -- not only when it decides to click --
 * so a panel that happens to start out already collapsed still gets marked,
 * instead of staying eligible to be mistaken for an unhandled first connect
 * (and wrongly re-collapsed) after a later reconnect re-expands it.
 */
(function () {
    'use strict';

    const INITIALIZED_ATTR = 'data-openstax-collapse-block-initialized';

    class OpenStaxCollapseBlockController extends window.StimulusModule.Controller {
        connect() {
            const panel = this.element.closest('[data-panel]');
            if (!panel || panel.hasAttribute(INITIALIZED_ATTR)) {
                return;
            }
            const toggle = panel.querySelector('[data-panel-toggle]');
            if (!toggle) {
                return;
            }
            // Mark as soon as a toggle exists, regardless of whether we
            // collapse below -- a panel that starts out already collapsed
            // still needs to be marked, or a later reconnect could mistake
            // it (once the editor has since expanded it) for a first
            // connect and collapse it again.
            panel.setAttribute(INITIALIZED_ATTR, '');
            if (toggle.getAttribute('aria-expanded') === 'true') {
                toggle.click();
            }
        }
    }

    window.wagtail.app.register('openstax-collapse-block', OpenStaxCollapseBlockController);
})();
