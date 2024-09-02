document.addEventListener("DOMContentLoaded", function () {
    const createItemButton = document.getElementById('createItemButton');

    const itemModalElement = document.getElementById('itemModal');
    const itemModalContentElement = document.getElementById('itemModalContent');

    const url = createItemButton.getAttribute("href");

    itemModalElement.addEventListener('hidden.bs.modal', function (event) {
      itemModalContentElement.innerHTML = ''
    });

    createItemButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        itemModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(itemModalElement, {});
        modal.show();

        const selectVatAjaxElement = document.getElementById("id_vat");

        const optionVatAjaxElement = createCountryOptionElement("new_vat", "Dodaj nowy var", true);
        selectVatAjaxElement.appendChild(optionVatAjaxElement);

        const cancelVatAjaxElement = document.getElementById("cancelVatButton");
        const saveVatAjaxElement = document.getElementById("saveVatButton");

        const newVatAjaxInput = document.createElement("input");
        newVatAjaxInput.classList.add("form-control");

        selectVatAjaxElement.addEventListener("change", () => {
            if (selectVatAjaxElement.value === "new_country") {
                cancelVatAjaxElement.classList.remove("d-none");
                saveVatAjaxElement.classList.remove("d-none");
                selectVatAjaxElement.classList.add("d-none");
                selectVatAjaxElement.parentElement.appendChild(newVatAjaxInput);
                newVatAjaxInput.classList.remove("d-none");
            }
        });

        const hideVatEditMode = () => {
            cancelVatAjaxElement.classList.add("d-none");
            saveVatAjaxElement.classList.add("d-none");
            newVatAjaxInput.classList.add("d-none");
            selectVatAjaxElement.classList.remove("d-none");
        };

        cancelVatAjaxElement.addEventListener("click", (e) => {
            e.preventDefault();
            hideVatEditMode();
            selectVatAjaxElement.value = "";
            newVatAjaxInput.value = "";
        });

        saveVatAjaxElement.addEventListener("click", async (e) => {
            e.preventDefault();

            const vatAjaxErrors = document.getElementById('id_vat_errors');
            if (vatAjaxErrors) {
                    vatAjaxErrors.parentElement.removeChild(vatAjaxErrors);
                }

            const urlVatAjax = saveVatAjaxElement.getAttribute("href");
            const csrfVatAjaxElement = document.getElementsByName("csrfmiddlewaretoken")[0];

            const data = new FormData();
            data.set("country", newVatAjaxInput.value);
            data.set("csrfmiddlewaretoken", csrfVatAjaxElement.value);

            const response = await fetch(urlVatAjax, {
                method: "POST",
                body: data
            });
            const json = await response.json();

            if (json['success'] === false) {

                const rowAjaxContainer = selectVatAjaxElement.parentElement.parentElement;

                const errorAjaxElement = document.createElement('div');
                errorAjaxElement.setAttribute('id', 'id_vat_errors');
                errorAjaxElement.setAttribute('class', 'row');

                const errorAjaxContainer = document.createElement('div');
                errorAjaxContainer.setAttribute('class', 'col-12 col-md-6 offset-md-6 text-danger');
                errorAjaxElement.appendChild(errorAjaxContainer);

                const errorUlAjaxContainer = document.createElement('ul');
                errorUlAjaxContainer.setAttribute('class', 'errorlist');
                errorAjaxContainer.appendChild(errorUlAjaxContainer);

                const vatAjaxErrors = json['errors']['vat'];

                vatAjaxErrors.forEach((value) => {
                    const errorLiAjaxElement = document.createElement('li');
                    const errorAjaxLabel = document.createTextNode(value);
                    errorLiAjaxElement.appendChild(errorAjaxLabel);

                    errorUlAjaxContainer.appendChild(errorLiAjaxElement);
                });

                rowAjaxContainer.parentElement.insertBefore(errorAjaxElement, rowAjaxContainer.nextSibling);
            } else {
                hideVatEditMode();

                const newVatAjaxOption = createCountryOptionElement(json.id, json.name);
                selectVatAjaxElement.appendChild(newVatAjaxOption);

                selectVatAjaxElement.value = json.id.toString();
                newVatAjaxInput.value = "";
            }

        });

        const createItemSaveButton = document.getElementById('createItemSaveButton');

        createItemSaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const form = itemModalContentElement.getElementsByTagName('form')[0];
            const data = new FormData(form);

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if (json.success) {
                const selectElement = document.getElementById('id_item');

                const optionElement = document.createElement('option');
                optionElement.setAttribute('value', json.id);

                const optionNameElement = document.createTextNode(json.name);

                optionElement.appendChild(optionNameElement);
                selectElement.appendChild(optionElement);

                selectElement.value = json.id.toString();

                modal.hide();
            }
        });
    });
});