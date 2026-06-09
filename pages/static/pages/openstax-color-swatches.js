/*
 * OpenStax brand-swatch picker for the wagtail-color-panel colour widget.
 *
 * Implemented as a Wagtail/Stimulus controller (the idiomatic client-side
 * extension mechanism — see Wagtail "Extending client-side"). It is attached via
 * `data-controller="color-input openstax-color-swatches"` on the colour text
 * input (see OpenStaxColorInputWidget.build_attrs). Stimulus runs connect() when
 * the element enters the DOM and disconnect() when it leaves — for the initial
 * page, for StreamField/InlinePanel blocks added at runtime, and inside modals —
 * so no MutationObserver or manual re-scan is needed.
 *
 * The palette arrives as a Stimulus Array value (`data-openstax-color-swatches-
 * palette-value`), set in Python from OPENSTAX_BRAND_COLORS.
 */
(function () {
    'use strict';

    const HEX_RE = /^#[0-9a-f]{6}$/i;

    function normalizeHex(value) {
        return typeof value === 'string' ? value.trim().toUpperCase() : '';
    }

    // Group colours by family (first word of the label), preserving palette order.
    function groupByFamily(colors) {
        const groups = new Map();
        colors.forEach((color) => {
            const value = normalizeHex(color && color.value);
            if (!value) {
                return;
            }
            const family = ((color.label || 'Other').split(' ')[0]);
            if (!groups.has(family)) {
                groups.set(family, []);
            }
            groups.get(family).push({ label: color.label || value, value: value });
        });
        return groups;
    }

    class OpenStaxColorSwatchesController extends window.StimulusModule.Controller {
        // Palette is supplied by Python; default keeps the controller safe if absent.
        static values = { palette: { type: Array, default: [] } };

        connect() {
            this.textInput = this.element;
            this.wrapper = this.textInput.closest('.color-input-widget');
            if (!this.wrapper) {
                return;
            }
            this.colorInput = this.wrapper.querySelector('input[type="color"]');

            const groups = groupByFamily(this.paletteValue);
            if (!groups.size) {
                return;
            }

            // The widget shows empty values as the literal "None"; clear it so the
            // native colour chip stays valid. No event dispatched -> not dirty.
            if (this.textInput.value && !HEX_RE.test(this.textInput.value.trim())) {
                this.textInput.value = '';
                if (this.colorInput) {
                    this.colorInput.value = '#000000';
                }
            }

            this.swatches = [];
            this.panel = this.buildPanel(groups);
            this.wrapper.insertAdjacentElement('afterend', this.panel);

            this.onValueChange = this.syncSelection.bind(this);
            this.textInput.addEventListener('input', this.onValueChange);
            if (this.colorInput) {
                this.colorInput.addEventListener('input', this.onValueChange);
            }
            this.syncSelection();
        }

        disconnect() {
            if (this.onValueChange) {
                this.textInput.removeEventListener('input', this.onValueChange);
                if (this.colorInput) {
                    this.colorInput.removeEventListener('input', this.onValueChange);
                }
            }
            if (this.panel) {
                this.panel.remove();
            }
            this.swatches = [];
        }

        // Set the value and let the package's color-input controller mirror it into
        // the native <input type="color"> via its 'input' listener.
        applyColor(value) {
            this.textInput.value = value;
            this.textInput.dispatchEvent(new Event('input', { bubbles: true }));
        }

        buildPanel(groups) {
            const panel = document.createElement('div');
            panel.className = 'openstax-color-panel';

            // Selected-colour readout, boxed off at the top.
            const readout = document.createElement('div');
            readout.className = 'openstax-color-readout';

            this.readoutLabel = document.createElement('span');
            this.readoutLabel.className = 'openstax-color-readout-label';
            this.readoutLabel.textContent = 'Selected';

            this.readoutDot = document.createElement('span');
            this.readoutDot.className = 'openstax-color-readout-dot';

            this.readoutText = document.createElement('span');
            this.readoutText.className = 'openstax-color-readout-text';

            readout.appendChild(this.readoutLabel);
            readout.appendChild(this.readoutDot);
            readout.appendChild(this.readoutText);
            this.readout = readout;
            panel.appendChild(readout);

            const title = document.createElement('p');
            title.className = 'openstax-color-title';
            title.textContent = 'OpenStax brand colors';
            panel.appendChild(title);

            const grid = document.createElement('div');
            grid.className = 'openstax-color-grid';
            panel.appendChild(grid);

            groups.forEach((colors, family) => {
                const group = document.createElement('div');
                group.className = 'openstax-color-group';

                const familyLabel = document.createElement('span');
                familyLabel.className = 'openstax-color-family';
                familyLabel.textContent = family;
                group.appendChild(familyLabel);

                const row = document.createElement('div');
                row.className = 'openstax-color-swatches';

                colors.forEach((color) => {
                    row.appendChild(this.buildSwatch(color));
                });

                group.appendChild(row);
                grid.appendChild(group);
            });

            return panel;
        }

        buildSwatch(color) {
            const tooltip = color.label + ' · ' + color.value;

            // <span role="button"> rather than <button> avoids Wagtail's global
            // button reset; all visuals come from the stylesheet.
            const swatch = document.createElement('span');
            swatch.className = 'openstax-color-swatch';
            swatch.setAttribute('role', 'button');
            swatch.setAttribute('tabindex', '0');
            swatch.dataset.colorValue = color.value;
            swatch.dataset.colorLabel = color.label;
            swatch.title = tooltip;
            swatch.setAttribute('aria-label', tooltip);
            swatch.setAttribute('aria-pressed', 'false');
            // The only inline style is data, not styling: the CSS reads it via
            // `background-color: var(--swatch-color)`.
            swatch.style.setProperty('--swatch-color', color.value);

            swatch.addEventListener('click', () => this.applyColor(color.value));
            swatch.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
                    event.preventDefault();
                    this.applyColor(color.value);
                }
            });

            this.swatches.push(swatch);
            return swatch;
        }

        syncSelection() {
            const current = normalizeHex(this.textInput.value);
            let matchedLabel = null;

            this.swatches.forEach((swatch) => {
                const isSelected = swatch.dataset.colorValue === current;
                swatch.classList.toggle('is-selected', isSelected);
                swatch.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
                if (isSelected) {
                    matchedLabel = swatch.dataset.colorLabel;
                }
            });

            if (!current) {
                this.readout.classList.add('is-empty');
                this.readoutDot.style.removeProperty('--swatch-color');
                this.readoutText.textContent = 'No color selected';
                return;
            }

            this.readout.classList.remove('is-empty');
            this.readoutDot.style.setProperty('--swatch-color', current);
            this.readoutText.innerHTML = matchedLabel
                ? '<strong>' + matchedLabel + '</strong> · ' + current
                : '<strong>Custom</strong> · ' + current;
        }
    }

    window.wagtail.app.register('openstax-color-swatches', OpenStaxColorSwatchesController);
})();
