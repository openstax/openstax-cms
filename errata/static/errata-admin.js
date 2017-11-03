(function($) {
    $(function() {
        var bookField = $('#id_book'),
            is_assessment = $('#id_is_assessment_errata');

        function toggleVerified(bookField) {
            var bookArray = [33, 32, 31, 47];
            jQuery.inArray(bookField, bookArray) ? is_assessment.show() : is_assessment.hide();
        }

        // show/hide on load based on pervious value of selectField
        toggleVerified(bookField.val());

        // show/hide on change
        bookField.change(function() {
            toggleVerified($(this).val());
        });
    });
})(django.jQuery);