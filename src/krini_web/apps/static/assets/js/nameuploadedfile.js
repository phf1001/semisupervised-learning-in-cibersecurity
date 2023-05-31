var input = document.getElementById('uploaded_test_csv');
var infoArea = document.getElementById('uploaded_filename');

input.addEventListener('change', showFileName);

function showFileName(event) {
    var input = event.srcElement;
    var fileName = input.files[0].name;
    infoArea.textContent = fileName;
}

var input_train = document.getElementById('uploaded_train_csv');

if (input_train) {
    var infoArea_train = document.getElementById('uploaded_filename_train');
    input_train.addEventListener('change', showFileName);

    function showFileName(event) {
        var input = event.srcElement;
        var fileName = input.files[0].name;
        infoArea_train.textContent = fileName;
    }
}