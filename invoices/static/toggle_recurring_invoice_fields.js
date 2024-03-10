document.addEventListener("DOMContentLoaded", function () {
    const isRecurringCheckbox = document.getElementById('id_is_recurring');
    const invoiceNumberInput = document.getElementById('id_invoice_number');
    const isLastDayContainerElement = document.getElementById('id_is_last_day').parentElement;
    const isPaidContainerElement = document.getElementById('isPaidContainerElement');

    if (isRecurringCheckbox.checked) {
        invoiceNumberInput.disabled = true;
        isLastDayContainerElement.classList.remove('d-none');
        isPaidContainerElement.classList.add('d-none');
    } else {
        invoiceNumberInput.disabled = false;
        isLastDayContainerElement.classList.add('d-none');
        isPaidContainerElement.classList.remove('d-none');
    }

    isRecurringCheckbox.addEventListener("change", (e) => {
        e.preventDefault();

        if (isRecurringCheckbox.checked) {
            invoiceNumberInput.disabled = true;
            isLastDayContainerElement.classList.remove('d-none');
            isPaidContainerElement.classList.add('d-none');
        } else {
            invoiceNumberInput.disabled = false;
            isLastDayContainerElement.classList.add('d-none');
            isPaidContainerElement.classList.remove('d-none');
        }
    });

    const isLastDayElement = document.getElementById('id_is_last_day');
    const saleDateInput = document.getElementById('id_sale_date').value;
    const saleDateContainer = document.getElementById("saleDateContainer");

    isLastDayElement.addEventListener("change", (e) =>{
        e.preventDefault();

        const lastDayErrors = document.getElementById('id_last_day_errors');
        if (lastDayErrors) {
            lastDayErrors.parentElement.removeChild(lastDayErrors);
        }

        if (isLastDayElement.checked) {
            if (!isLastDayOfMonth(saleDateInput)) {
                const errorElement = document.createElement('div');
                errorElement.setAttribute('id', 'id_last_day_errors');
                errorElement.setAttribute('class', 'row');

                const errorContainer = document.createElement('div');
                errorContainer.setAttribute('class', 'col-auto offset-5 text-danger');
                errorElement.appendChild(errorContainer);

                const errorUlContainer = document.createElement('ul');
                errorUlContainer.setAttribute('class', 'errorlist');
                errorContainer.appendChild(errorUlContainer);

                const errorLiElement = document.createElement('li');
                const errorLabel = document.createTextNode("To nie jest ostatni dzień miesiąca.");
                errorLiElement.appendChild(errorLabel);

                errorUlContainer.appendChild(errorLiElement);

                saleDateContainer.parentElement.insertBefore(errorElement, saleDateContainer.nextSibling);
            }
        }
    });
});
