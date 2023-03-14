const selectBtn = document.querySelector('.select-btn');
items = document.querySelectorAll('.item');

selectBtn.addEventListener('click', () => {
    selectBtn.classList.toggle('open');
});

items.forEach(item => {

    item.addEventListener('click', () => {

        item.classList.toggle("checked");
        let checked = document.querySelectorAll('.checked');
        btnText = document.querySelector('.btn-text');
        
        if (checked && checked.length > 0) {
            btnText.innerText = `Selected (${checked.length})`;
        } else {
            btnText.innerText = "Select your models";
        }
    })
})

var saveButton = document.getElementById('btn-submit');

saveButton.addEventListener('click', function () {

    let checked = document.querySelectorAll('.checked');
    let selected_names = [];

    for (var i = 0; i < checked.length; i++) {
        selected_names.push(checked[i].value);
    }

    document.getElementById('selected_models').value = selected_names;
});