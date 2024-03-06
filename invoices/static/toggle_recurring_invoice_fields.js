document.addEventListener("DOMContentLoaded", function () {
    const isRecurringCheckbox = document.getElementById('id_is_recurring');
    const invoiceNumberInput = document.getElementById('id_invoice_number');
    const isLastDayContainerElement = document.getElementById('id_is_last_day').parentElement;
    const isPaidContainerElement = document.getElementById('isPaidContainerElement');


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
});
