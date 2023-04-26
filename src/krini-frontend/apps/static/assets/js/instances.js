const downloadBtn = document.getElementById('btn-descarga-csv');
var checkboxes_instances = document.querySelectorAll('input[type=checkbox]');

downloadBtn.addEventListener('click', function () {

    var checked = [].filter.call(checkboxes_instances, function (elem) {
        return elem.checked;
    });

    for (var i = 0; i < checked.length; i++) {
        checked[i] = checked[i].value;
    }

    if (checked.length == 0) {
        console.log('No hay checkboxes seleccionados');
    } else {
        console.log(checked);
    }
});

function updateForm(individual_instance, button_pressed, page, previous_page) {

    if (individual_instance != null) {
        document.instances_form.individual_instance.value = individual_instance;
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