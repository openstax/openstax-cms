django.jQuery(function ($) {
    $(document).ready(function(){
        $('form').submit(function() {
            var status = document.getElementById("id_status");
            var resolution = document.getElementById("id_resolution");
            
            if (!status.options[status.selectedIndex].defaultSelected || !resolution.options[resolution.selectedIndex].defaultSelected) {
                var c = confirm("User who sent this errata will receive an email. Do you still want to continue?");
                return c;
            } else {
                return true;
            }
            
        });
    })
})