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
            if (!toggle || toggle.getAttribute('aria-expanded') !== 'true') {
                return;
            }
            // Mark only once we know we're actually collapsing -- if the
            // toggle isn't there yet (or already collapsed) this leaves the
            // panel unmarked so a later connect() can still try.
            panel.setAttribute(INITIALIZED_ATTR, '');
            toggle.click();
        }
    }

    window.wagtail.app.register('openstax-collapse-block', OpenStaxCollapseBlockController);
})();
