$(function() {
    $(document).ready(function() {
        $('#searchSubmitButton').click(function () {
            $('form#quiz-search-form').submit();
            return false;
        });
    });
});