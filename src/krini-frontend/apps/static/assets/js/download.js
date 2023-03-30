const downloadBtn = document.getElementById('btn-descarga-csv');
var checkboxes_instances = document.querySelectorAll('input[type=checkbox]'); 

downloadBtn.addEventListener('click', function() {

    var checked = [].filter.call( checkboxes_instances, function( elem ) {
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