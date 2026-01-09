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
                
                $layoutField.find('input[type="hidden"][name*="type"], input[type="hidden"][name*="block_type"]').each(function() {
                    if ($(this).val() === 'landing') {
                        hasLandingPage = true;
                        return false; // break
                    }
                });
                
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
        });
    };
    
    // Start initialization
    init();
})();
