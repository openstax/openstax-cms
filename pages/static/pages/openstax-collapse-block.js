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
 */
(function () {
    'use strict';

    class OpenStaxCollapseBlockController extends window.StimulusModule.Controller {
        connect() {
            const panel = this.element.closest('[data-panel]');
            if (!panel) {
                return;
            }
            const toggle = panel.querySelector('[data-panel-toggle]');
            if (!toggle || toggle.getAttribute('aria-expanded') !== 'true') {
                return;
            }
            toggle.click();
        }
    }

    window.wagtail.app.register('openstax-collapse-block', OpenStaxCollapseBlockController);
})();
