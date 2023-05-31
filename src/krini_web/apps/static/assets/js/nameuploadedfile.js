var input = document.getElementById('uploaded_test_csv');

if (input) {
    var infoArea = document.getElementById('uploaded_filename');

    input.addEventListener('change', showFileName);

    function showFileName(event) {
        var input = event.srcElement;
        var fileName = input.files[0].name;
        infoArea.textContent = fileName;
    }
}

var input_train = document.getElementById('train_file');

if (input_train) {
    var infoArea_train = document.getElementById('uploaded_filename_train');
    input_train.addEventListener('change', showFileName);

    function showFileName(event) {
        var input = event.srcElement;
        var fileName = input.files[0].name;
        infoArea_train.textContent = fileName;
    }
}

var input_test = document.getElementById('test_file');

if (input_test) {
    var infoArea_test = document.getElementById('uploaded_filename');
    input_test.addEventListener('change', showFileName);

    function showFileName(event) {
        var input = event.srcElement;
        var fileName = input.files[0].name;
        infoArea_test.textContent = fileName;
    }
}