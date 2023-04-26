function updateForm(individual_model, button_pressed, page, previous_page) {

    if (individual_model != null) {
        document.models_form.individual_model.value = individual_model;
    }

    if (button_pressed != null) {
        document.models_form.button_pressed.value = button_pressed;
    }

    if (page != null) {
        document.models_form.selected_page.value = page;
    }

    if (previous_page != null) {
        document.models_form.previous_page.value = previous_page;
    }
    return true;
}