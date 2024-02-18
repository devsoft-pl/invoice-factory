document.addEventListener("DOMContentLoaded", function () {
    const createVatButton = document.getElementById('createVatButton');

    const vatModalElement = document.getElementById('vatModal');
    const vatModalContentElement = document.getElementById('vatModalContent');

    const url = createVatButton.getAttribute("href");

    createVatButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        vatModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(vatModalElement, {});
        modal.show();

        const createVatSaveButton = document.getElementById('createVatSaveButton');

        createVatSaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const form = vatModalContentElement.getElementsByTagName('form')[0]

            const data = new FormData(form)

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if(json.success) {
                const selectElement = document.getElementById('id_vat');

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