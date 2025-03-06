document.addEventListener("DOMContentLoaded", function () {
    const dayInput = document.getElementById('id_day');
    const isLastDayElement = document.getElementById('id_is_last_day');
    const errorContainer = document.getElementById('id_last_day_errors_container');

    function removeLastDayError() {
        errorContainer.innerHTML = ''; // Usuwamy wszystkie błędy
    }

    function showLastDayError() {
        const errorElement = document.createElement('div');
        errorElement.classList.add('row');

        const errorContent = document.createElement('div');
        errorContent.classList.add('col-12', 'col-md-6', 'offset-md-6', 'text-danger');

        const errorUl = document.createElement('ul');
        errorUl.classList.add('errorlist');

        const errorLi = document.createElement('li');
        errorLi.textContent = "To nie jest ostatni dzień miesiąca.";
        errorUl.appendChild(errorLi);
        errorContent.appendChild(errorUl);
        errorElement.appendChild(errorContent);

        errorContainer.appendChild(errorElement);
    }

    function validateLastDay() {
        removeLastDayError();
        const dayValue = parseInt(dayInput.value, 10);

        if (isLastDayElement.checked && (!dayValue || !isLastDay(dayValue))) {
            showLastDayError();
        }
    }

    isLastDayElement.addEventListener("change", validateLastDay);
    dayInput.addEventListener("change", validateLastDay);
});