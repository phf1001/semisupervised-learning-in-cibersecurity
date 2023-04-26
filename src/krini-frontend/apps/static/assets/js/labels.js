
$(document).ready(function () {
    $('#labels').tokenfield({
        autocomplete: {
            source: $('#instance-tags').data('instance-tags'),
            delay: 100
        },
        showAutocompleteOnFocus: true
    });

    $('#reg_form').on('submit', function (event) {
        event.preventDefault();
        var form_data = $(this).serialize();
        $('#submit').attr("disabled", "disabled");
        $.ajax({
            url: "/ajax_add",
            method: "POST",
            data: form_data,
            beforeSend: function () {
                $('#submit').val('Submitting...');
            },
            success: function (data) {
                if (data != '') {
                    $('#labels').tokenfield('setTokens', []);
                    $('#success_message').html(data);
                    $('#submit').attr("disabled", false);
                    $('#submit').val('Submit');
                }
            }
        });
        setInterval(function () {
            $('#success_message').html('');
        }, 5000);

    });
});