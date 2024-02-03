document.addEventListener("DOMContentLoaded", function() {
    const createCountryButton = document.getElementById('createCountryButton');

    const countryModalElement = document.getElementById('countryModal');
    const countryModalContentElement = document.getElementById('countryModalContent');

    const url = createCountryButton.getAttribute("href");

    createCountryButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        countryModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(countryModalElement, {});
        modal.show();

        const createCountrySaveButton = document.getElementById('createCountrySaveButton');

        createCountrySaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const form = countryModalContentElement.getElementsByTagName('form')[0]

            const data = new FormData(form)

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if(json.success) {
                const selectElement = document.getElementById('id_country');

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