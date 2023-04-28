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
            btnText.innerText = `(${checked.length})`;
        } else {
            btnText.innerText = "";
        }
    })
})

select_all = document.getElementById("select-all");
select_all.addEventListener('click', () => { 

    items.forEach(item => {
        if (!(item.classList.contains("checked"))) {
            item.classList.toggle("checked");
        }
    })
    btnText = document.querySelector('.btn-text');
    btnText.innerText = `(${items.length})`;
})

deselect_all = document.getElementById("deselect-all");
deselect_all.addEventListener('click', () => { 

    items.forEach(item => {
        if (item.classList.contains("checked")) {
            item.classList.toggle("checked");
        }
    })
    btnText = document.querySelector('.btn-text');
    btnText.innerText = "";
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