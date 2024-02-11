document.addEventListener("DOMContentLoaded", function () {
    const createCurrencyButton = document.getElementById('createCurrencyButton');

    const currencyModalElement = document.getElementById('currencyModal');
    const currencyModalContentElement = document.getElementById('currencyModalContent');

    const url = createCurrencyButton.getAttribute("href");

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

            const form = currencyModalContentElement.getElementsByTagName('form')[0]

            const data = new FormData(form)

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if (json.success) {
                const selectElement = document.getElementById('id_currency');

                const optionElement = document.createElement('option');
                optionElement.setAttribute('value', json.id);

                const optionNameElement = document.createTextNode(json.name);

                optionElement.appendChild(optionNameElement)
                selectElement.appendChild(optionElement);

                selectElement.value = json.id.toString()

                modal.hide();
            }
        })
    });
});