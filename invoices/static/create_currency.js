document.addEventListener("DOMContentLoaded", function () {
    const createCurrencyButton = document.getElementById('createCurrencyButton');

    const currencyModalElement = document.getElementById('currencyModal');
    const currencyModalContentElement = document.getElementById('currencyModalContent');

    const url = createCurrencyButton.getAttribute("href");

    currencyModalElement.addEventListener('hidden.bs.modal', function (event) {
      currencyModalContentElement.innerHTML = ''
    });

    createCurrencyButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        currencyModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(currencyModalElement, {});
        modal.show();

        const createCurrencySaveButton = document.getElementById('createCurrencySaveButton');

        createCurrencySaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const currencyErrors = document.getElementById('id_code_errors');
            if (currencyErrors) {
                    currencyErrors.parentElement.removeChild(currencyErrors);
                }

            const form = currencyModalContentElement.getElementsByTagName('form')[0];

            const data = new FormData(form);

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

             if (json['success'] === false) {

                 const selectCurrencyElement = document.getElementById("id_code");
                 const rowContainer = selectCurrencyElement.parentElement.parentElement;

                 const errorElement = document.createElement('div');
                 errorElement.setAttribute('id', 'id_code_errors');
                 errorElement.setAttribute('class', 'row');

                 const errorContainer = document.createElement('div');
                 errorContainer.setAttribute('class', 'col-12 offset-md-6 text-danger');
                 errorElement.appendChild(errorContainer);

                 const errorUlContainer = document.createElement('ul');
                 errorUlContainer.setAttribute('class', 'errorlist');
                 errorContainer.appendChild(errorUlContainer);

                 const currencyErrors = json['errors']['code'];

                 currencyErrors.forEach((value) => {
                    const errorLiElement = document.createElement('li');
                    const errorLabel = document.createTextNode(value);
                    errorLiElement.appendChild(errorLabel);

                    errorUlContainer.appendChild(errorLiElement);
                });

                rowContainer.parentElement.insertBefore(errorElement, rowContainer.nextSibling);
             } else {
                const selectElement = document.getElementById('id_currency');

                const optionElement = document.createElement('option');
                optionElement.setAttribute('value', json.id);

                const optionNameElement = document.createTextNode(json.name);

                optionElement.appendChild(optionNameElement);
                selectElement.appendChild(optionElement);

                selectElement.value = json.id.toString();

                modal.hide();
            }
        })
    });
});