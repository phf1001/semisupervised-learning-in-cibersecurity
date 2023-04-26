
function updateForm(report_number, button_pressed, page, previous_page) {

    if (report_number != null) {
        document.instances_form.report_number.value = report_number;
    }

    if (button_pressed != null) {
        document.instances_form.button_pressed.value = button_pressed;
    }

    if (page != null) {
        document.instances_form.selected_page.value = page;
    }

    if (previous_page != null) {
        document.instances_form.previous_page.value = previous_page;
    }
    return true;
}
