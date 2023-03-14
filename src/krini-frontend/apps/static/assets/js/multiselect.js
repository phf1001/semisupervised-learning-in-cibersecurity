const selectBtn = document.querySelector('.select-btn');
items = document.querySelectorAll('.item');

selectBtn.addEventListener('click', () => {
    selectBtn.classList.toggle('open');
});

items.forEach(item => {
    item.addEventListener('click', () => {
        item.classList.toggle("checked");

        let checked = document.querySelectorAll('.checked');
        let checked_names = document.querySelectorAll('.checked').forEach(item => item.innerText);

        btnText = document.querySelector('.btn-text');
        
        if (checked && checked.length > 0) {
            btnText.innerText = `Selected (${checked.length})`;
            
        } else {
            btnText.innerText = "Select your models";
        }

        let selected_names = [];

        for(var i=0; i<checked.length; i++){
            selected_names.push(checked[i].innerText);
        }

        console.log(selected_names)

    })
})