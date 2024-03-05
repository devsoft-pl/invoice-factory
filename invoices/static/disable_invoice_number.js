document.addEventListener("DOMContentLoaded", function () {
    const isRecurringCheckbox = document.getElementById('id_is_recurring');
    const invoiceNumberInput = document.getElementById('id_invoice_number');


    isRecurringCheckbox.addEventListener("change", (e) => {
        e.preventDefault();

        invoiceNumberInput.disabled = !!isRecurringCheckbox.checked;
    });
});
