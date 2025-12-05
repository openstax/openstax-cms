(function() {
    // Get jQuery - try django.jQuery first (Django admin), then fall back to regular jQuery
    var getJQuery = function() {
        if (typeof django !== 'undefined' && django.jQuery) {
            return django.jQuery;
        } else if (typeof jQuery !== 'undefined') {
            return jQuery;
        } else if (typeof $ !== 'undefined') {
            return $;
        }
        return null;
    };
    
    // Wait for jQuery to be available
    var init = function() {
        var $ = getJQuery();
        if (!$) {
            // jQuery not ready yet, try again
            setTimeout(init, 50);
            return;
        }
        
        $(document).ready(function(){
            function checkAndToggleSchoolField() {
                // Find the layout StreamField container
                // Wagtail StreamFields have a data-contentpath attribute
                var $layoutField = $('[data-contentpath="layout"]');
                
                if ($layoutField.length === 0) {
                    return;
                }
                
                // Check if there's a block with type "landing" (displayed as "Landing Page")
                var hasLandingPage = false;
                
                // Method 1: Check for the block type label "Landing Page" in the layout field
                var $landingPageLabel = $layoutField.find('.c-sf-block_type').filter(function() {
                    return $(this).text().trim() === 'Landing Page';
                });
                
                if ($landingPageLabel.length > 0) {
                    hasLandingPage = true;
                } else {
                    // Method 2: Check hidden inputs for block type value "landing"
                    $layoutField.find('input[type="hidden"][name*="type"], input[type="hidden"][name*="block_type"]').each(function() {
                        if ($(this).val() === 'landing') {
                            hasLandingPage = true;
                            return false; // break
                        }
                    });
                    
                    // Method 3: Check StreamField value directly via JSON data
                    if (!hasLandingPage) {
                        var $hiddenInput = $layoutField.find('input[type="hidden"][name*="layout"]');
                        if ($hiddenInput.length > 0) {
                            try {
                                var streamValue = JSON.parse($hiddenInput.val() || '[]');
                                if (Array.isArray(streamValue) && streamValue.length > 0) {
                                    hasLandingPage = streamValue[0].type === 'landing';
                                }
                            } catch (e) {
                                // JSON parse failed, continue with other methods
                            }
                        }
                    }
                }
                
                // Find the School field panel
                // Try multiple selectors based on Wagtail panel structure
                var $schoolPanel = null;
                
                // Try by ID first (based on image description showing panel IDs)
                var schoolPanelIds = [
                    '#panel-child-content-school',
                    '#panel-child-content-school-section',
                    '[id*="panel"][id*="school"]'
                ];
                
                for (var i = 0; i < schoolPanelIds.length; i++) {
                    var $found = $(schoolPanelIds[i]).closest('.w-panel, section.w-panel');
                    if ($found.length > 0) {
                        $schoolPanel = $found;
                        break;
                    }
                }
                
                // If not found by ID, try finding by label/heading text "School"
                // Scope search to the form container to avoid false matches
                if (!$schoolPanel || $schoolPanel.length === 0) {
                    var $formContainer = $('.w-form-width, .w-form, [class*="wagtail"]').first();
                    if ($formContainer.length === 0) {
                        $formContainer = $('form').first();
                    }
                    
                    $formContainer.find('label, .w-panel_heading, h2, [data-panel-heading-text]').each(function() {
                        var $el = $(this);
                        var text = $el.text().trim();
                        if (text.toLowerCase() === 'school') {
                            $schoolPanel = $el.closest('.w-panel, section.w-panel');
                            if ($schoolPanel.length > 0) {
                                return false; // break
                            }
                        }
                    });
                }
                
                // Last resort: try finding by data-contentpath
                if (!$schoolPanel || $schoolPanel.length === 0) {
                    $schoolPanel = $('[data-contentpath="school"]').closest('.w-panel, section.w-panel');
                }
                
                // Show or hide the School panel
                if ($schoolPanel && $schoolPanel.length > 0) {
                    if (hasLandingPage) {
                        $schoolPanel.show();
                    } else {
                        $schoolPanel.hide();
                    }
                }
            }
            
            // Check on page load
            checkAndToggleSchoolField();
            
            // Also check after a delay to ensure StreamField is fully initialized
            setTimeout(checkAndToggleSchoolField, 500);
            
            // Listen for StreamField changes (when blocks are added/removed/changed)
            // Wagtail triggers custom events on StreamField changes
            $(document).on('wagtail:stream-field-block-added wagtail:stream-field-block-removed wagtail:stream-field-block-moved', function() {
                setTimeout(checkAndToggleSchoolField, 100);
            });
            
            // Also listen for any changes in the layout field container
            var $layoutField = $('[data-contentpath="layout"]');
            if ($layoutField.length > 0) {
                // Use MutationObserver to watch for DOM changes in the layout field
                var observer = new MutationObserver(function(mutations) {
                    checkAndToggleSchoolField();
                });
                
                observer.observe($layoutField[0], {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    characterData: true
                });
            }
            
            // Fallback: Also check periodically (with debouncing)
            var checkTimeout;
            $(document).on('change click input', '[data-contentpath="layout"]', function() {
                clearTimeout(checkTimeout);
                checkTimeout = setTimeout(checkAndToggleSchoolField, 200);
            });
        });
    };
    
    // Start initialization
    init();
})();

